from icrawler.builtin import GoogleImageCrawler
from icrawler.downloader import ImageDownloader

class UrlCollector(ImageDownloader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collected_urls = []

    # Override the download method so it doesn't download anything
    def download(self, task, default_ext, timeout=5, **kwargs):
        url = task['file_url']
        self.collected_urls.append(url)
        return True  # Pretend the download succeeded
