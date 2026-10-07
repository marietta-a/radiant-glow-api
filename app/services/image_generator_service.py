from __future__ import annotations

import asyncio
import logging
import os
import time

import requests
from ddgs import DDGS
import time 

from app.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10
RATE_LIMIT_COOLDOWN = 60  # seconds a provider is skipped after a 429 / failure
CACHE_TTL = 60 * 60 * 6
CACHE_MAX_ENTRIES = 1000
DDG_PROXY_ATTEMPTS = 4
QUEUE_TIMEOUT = 45  # max seconds a request waits in the queue for provider capacity
PROVIDER_CONCURRENCY = 5  # simultaneous in-flight calls per provider
PRIORITY = {"wikimedia": 0, "duckduckgo": 2}  # lower is tried first; everything else is 1 (duckduckgo is slow/unreliable)


class RateLimitedError(Exception):
    pass


def _get_json(url: str, *, headers: dict | None = None, params: dict | None = None) -> dict:
    response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
    if response.status_code == 429:
        raise RateLimitedError(url)
    response.raise_for_status()
    return response.json()


# Each provider: (name, env var holding its API key or None, sync search function).
# Search functions are blocking and run in a worker thread.

def _search_duckduckgo(query: str, num_images: int) -> list[str]:
    # Optional proxy (http/https/socks5), e.g. DDG_PROXY=http://user-rotate:pass@p.webshare.io:80
    # With a rotating proxy every attempt gets a new IP, so retry: many datacenter IPs are blocked.
    proxy = os.environ.get("DDG_PROXY") or None
    attempts = DDG_PROXY_ATTEMPTS if proxy else 1
    for attempt in range(attempts):
        try:
            results = DDGS(proxy=proxy, timeout=15 if proxy else 5).images(query, max_results=num_images)
            return [r["image"] for r in results if "image" in r]
        except Exception:
            if attempt == attempts - 1:
                raise
    return []


def _search_pexels(query: str, num_images: int) -> list[str]:
    data = _get_json(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": os.environ["PEXELS_API_KEY"]},
        params={"query": query, "per_page": num_images},
    )
    return [p["src"]["large"] for p in data.get("photos", [])]


def _search_pixabay(query: str, num_images: int) -> list[str]:
    data = _get_json(
        "https://pixabay.com/api/",
        params={
            "key": os.environ["PIXABAY_API_KEY"],
            "q": query,
            "per_page": max(3, num_images),  # Pixabay minimum is 3
            "image_type": "photo",
            "safesearch": "true",
        },
    )
    return [h["largeImageURL"] for h in data.get("hits", [])][:num_images]


# Unsplash API guidelines require: hotlinking the returned URLs, crediting the photographer and
# Unsplash (with utm params) wherever the photo is shown, and pinging the photo's download_location
# endpoint when a photo is used. Credits are kept per image URL so callers can pass them to the UI.
UNSPLASH_APP_NAME = os.environ.get("UNSPLASH_APP_NAME", "radiant_glow")
_UTM = f"utm_source={UNSPLASH_APP_NAME}&utm_medium=referral"
_unsplash_credits: dict[str, dict] = {}


def _search_unsplash(query: str, num_images: int) -> list[str]:
    data = _get_json(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"},
        params={"query": query, "per_page": num_images},
    )
    urls = []
    for r in data.get("results", []):
        url = r["urls"]["regular"]  # keep the URL exactly as returned (hotlinking required)
        if len(_unsplash_credits) >= CACHE_MAX_ENTRIES * 2:
            _unsplash_credits.pop(next(iter(_unsplash_credits)))
        _unsplash_credits[url] = {
            "provider": "unsplash",
            "photographer": r["user"]["name"],
            "photographer_url": f"{r['user']['links']['html']}?{_UTM}",
            "photo_url": f"{r['links']['html']}?{_UTM}",
            "unsplash_url": f"https://unsplash.com/?{_UTM}",
            "download_location": r["links"]["download_location"],
        }
        urls.append(url)
    return urls


def get_image_credits(urls: list[str]) -> dict[str, dict]:
    """Attribution for any of these URLs that require it (currently Unsplash photos).

    The UI must display e.g. "Photo by <photographer> on <Unsplash>", linking both
    names to photographer_url and unsplash_url.
    """
    return {
        u: {k: v for k, v in _unsplash_credits[u].items() if k != "download_location"}
        for u in urls
        if u in _unsplash_credits
    }


def _ping_unsplash_download(download_location: str) -> None:
    try:
        requests.get(
            download_location,
            headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as e:
        logger.warning("Unsplash download tracking failed: %s", e)


def _track_unsplash_downloads(urls: list[str]) -> None:
    """Fire-and-forget download events for Unsplash photos being served."""
    loop = asyncio.get_running_loop()
    for u in urls:
        credit = _unsplash_credits.get(u)
        if credit:
            loop.run_in_executor(None, _ping_unsplash_download, credit["download_location"])


def _search_brave(query: str, num_images: int) -> list[str]:
    data = _get_json(
        "https://api.search.brave.com/res/v1/images/search",
        headers={"X-Subscription-Token": os.environ["BRAVE_API_KEY"], "Accept": "application/json"},
        params={"q": query, "count": num_images},
    )
    return [r["properties"]["url"] for r in data.get("results", []) if r.get("properties", {}).get("url")]


def _search_wikimedia(query: str, num_images: int) -> list[str]:
    data = _get_json(
        "https://commons.wikimedia.org/w/api.php",
        headers={"User-Agent": "radiant-glow-api/1.0"},
        params={
            "action": "query", "format": "json", "generator": "search",
            "gsrnamespace": 6, "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": num_images,
            "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1024,
        },
    )
    pages = data.get("query", {}).get("pages", {}).values()
    return [p["imageinfo"][0]["thumburl"] for p in sorted(pages, key=lambda p: p.get("index", 0)) if p.get("imageinfo")]


# name, env var for its key (None = keyless), search function, (max calls, per seconds).
# Limits sit just under each provider's free tier, so bursts queue up instead of hitting 429s.
# Unsplash demo apps get 50/hour; set UNSPLASH_REQUESTS_PER_HOUR=5000 after production approval.
_PROVIDERS = [
    ("duckduckgo", None, _search_duckduckgo, (10, 60)),
    ("wikimedia", None, _search_wikimedia, (60, 60)),
    ("pexels", "PEXELS_API_KEY", _search_pexels, (180, 3600)),
    ("pixabay", "PIXABAY_API_KEY", _search_pixabay, (80, 60)),
    ("unsplash", "UNSPLASH_ACCESS_KEY", _search_unsplash, (int(os.environ.get("UNSPLASH_REQUESTS_PER_HOUR", 45)), 3600)),
    ("brave", "BRAVE_API_KEY", _search_brave, (1, 1.1)),
]

_limiters = {name: RateLimiter(calls, period) for name, _key, _fn, (calls, period) in _PROVIDERS}
_blocked_until: dict[str, float] = {}
_cache: dict[tuple[str, int], tuple[float, list[str]]] = {}


class _Job:
    __slots__ = ("query", "num_images", "cache_key", "future", "tried", "last_error")

    def __init__(self, query: str, num_images: int, cache_key: tuple, future: asyncio.Future):
        self.query, self.num_images, self.cache_key, self.future = query, num_images, cache_key, future
        self.tried: set[str] = set()
        self.last_error: Exception | None = None


# One shared queue; one worker per provider pulls jobs from it whenever that provider has rate
# limit capacity, so faster/roomier providers naturally take more of the load.
_queue: asyncio.Queue | None = None
_worker_loop: asyncio.AbstractEventLoop | None = None
_worker_tasks: list[asyncio.Task] = []
_inflight: dict[tuple, asyncio.Future] = {}


def _is_configured(key_env: str | None) -> bool:
    return key_env is None or bool(os.environ.get(key_env))


def _configured_names() -> set[str]:
    return {name for name, key_env, _fn, _limit in _PROVIDERS if _is_configured(key_env)}


def _rank(name: str) -> int:
    return PRIORITY.get(name, 1)


def _eligible(job: _Job, name: str) -> bool:
    if name in job.tried:
        return False
    # Only after every healthy provider ranked above it (see PRIORITY) has been tried.
    now = time.monotonic()
    rank = _rank(name)
    higher = {
        n for n, key_env, _fn, _limit in _PROVIDERS
        if _rank(n) < rank and _is_configured(key_env) and _blocked_until.get(n, 0) <= now
    }
    return higher <= job.tried


def _ensure_workers() -> None:
    global _queue, _worker_loop
    loop = asyncio.get_running_loop()
    if _worker_loop is loop:
        return
    _queue = asyncio.Queue()
    _worker_loop = loop
    _inflight.clear()
    _worker_tasks.clear()
    for name, key_env, fn, (calls, period) in _PROVIDERS:
        if _is_configured(key_env):
            _worker_tasks.append(loop.create_task(_provider_worker(name, fn, _limiters[name])))


async def _provider_worker(name: str, fn, limiter: RateLimiter) -> None:
    slots = asyncio.Semaphore(PROVIDER_CONCURRENCY)
    while True:
        await slots.acquire()
        cooldown = _blocked_until.get(name, 0) - time.monotonic()
        if cooldown > 0:
            slots.release()
            await asyncio.sleep(cooldown)
            continue
        await limiter.wait_for_capacity()  # don't take work this provider can't serve yet
        job = await _queue.get()
        if job.future.done():
            slots.release()
            continue
        if not _eligible(job, name):
            _queue.put_nowait(job)
            slots.release()
            await asyncio.sleep(0.05)
            continue
        limiter.record()
        asyncio.create_task(_run_job(name, fn, job, slots))


async def _run_job(name: str, fn, job: _Job, slots: asyncio.Semaphore) -> None:
    urls = None
    try:
        urls = await asyncio.to_thread(fn, job.query, job.num_images)
    except Exception as e:
        job.last_error = e
        _blocked_until[name] = time.monotonic() + RATE_LIMIT_COOLDOWN
        logger.warning("Image provider %s failed (%s); cooling down", name, e)
    finally:
        slots.release()

    if urls:
        logger.info("Images for '%s' provided by %s (%d results)", job.query, name, len(urls))
        if len(_cache) >= CACHE_MAX_ENTRIES:
            _cache.pop(next(iter(_cache)))
        _cache[job.cache_key] = (time.monotonic(), urls)  # cached even if the caller already gave up
        if not job.future.done():
            job.future.set_result(urls)
        return

    job.tried.add(name)
    if job.future.done():
        return
    if _configured_names() - job.tried:
        _queue.put_nowait(job)  # another provider will pick it up
    elif job.last_error:
        job.future.set_exception(job.last_error)
    else:
        job.future.set_result([])


async def get_image_urls(query: str, num_images: int = 2) -> list[str]:
    """Return image URLs for a query, spread across providers without exceeding their rate limits.

    Requests go through a shared queue served by one worker per provider; each worker only takes
    work while its provider is under its rate limit (see _PROVIDERS), so bursts wait in the queue
    instead of triggering 429s. A provider that errors is cooled down and the job moves on to the
    next one. Identical in-flight queries are shared, and results are cached per (query, count).
    """
    if not isinstance(num_images, int) or num_images <= 0:
        raise ValueError("num_images must be a positive integer")

    cache_key = (query.strip().lower(), num_images)
    cached = _cache.get(cache_key)
    if cached and time.monotonic() - cached[0] < CACHE_TTL:
        logger.info("Images for '%s' served from cache", query)
        _track_unsplash_downloads(cached[1])
        return cached[1]

    _ensure_workers()
    future = _inflight.get(cache_key)
    if future is None:
        future = asyncio.get_running_loop().create_future()
        _inflight[cache_key] = future
        future.add_done_callback(lambda _f, k=cache_key: _inflight.pop(k, None))
        _queue.put_nowait(_Job(query, num_images, cache_key, future))

    try:
        # shield: if this caller times out the job still finishes and warms the cache for a retry
        urls = await asyncio.wait_for(asyncio.shield(future), QUEUE_TIMEOUT)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Timed out waiting for image provider capacity for '{query}'")
    _track_unsplash_downloads(urls)
    return urls


async def get_duckduckgo_image_urls(query: str, num_images: int = 2) -> list[str]:
    """Kept for backwards compatibility; now distributes across all providers."""
    return await get_image_urls(query, num_images)



async def get_image_url_if_available(query: str) -> str | None:
    """One image URL for the query, or None. See find_image_if_available."""
    return (await find_image_if_available(query))[0]


async def find_image_if_available(query: str) -> tuple[str | None, dict | None]:
    """(image URL, attribution) for the query; (None, None) if nothing is available.

    Never queues or waits for rate limit capacity: tries each configured, healthy provider that is
    under its rate limit right now (wikimedia first, duckduckgo last) and gives up when all are
    exhausted or fail. The attribution is set for Unsplash photos, which must be credited in the UI.
    """
    cache_key = (query.strip().lower(), 1)
    cached = _cache.get(cache_key)
    if cached and cached[1] and time.monotonic() - cached[0] < CACHE_TTL:
        return _served(cached[1][0])

    for name, key_env, fn, _limit in sorted(_PROVIDERS, key=lambda p: _rank(p[0])):
        if not _is_configured(key_env):
            continue
        if _blocked_until.get(name, 0) > time.monotonic() or not _limiters[name].try_acquire():
            continue
        try:
            urls = await asyncio.to_thread(fn, query, 1)
        except Exception as e:
            _blocked_until[name] = time.monotonic() + RATE_LIMIT_COOLDOWN
            logger.warning("Image provider %s failed (%s); cooling down", name, e)
            continue
        if urls:
            if len(_cache) >= CACHE_MAX_ENTRIES:
                _cache.pop(next(iter(_cache)))
            _cache[cache_key] = (time.monotonic(), urls[:1])
            return _served(urls[0])
    return None, None


def _served(url: str) -> tuple[str, dict | None]:
    _track_unsplash_downloads([url])
    return url, get_image_credits([url]).get(url)
