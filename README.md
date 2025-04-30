---
title: AI Food Classifier 🍱
emoji: 🥗
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: "5.28.0"
app_file: app/app.py
pinned: false
---

# 🍱 AI Food Classifier – Hugging Face Space

This project is a simple Hugging Face Space that identifies food items in images and categorizes them into dishes based on bounding box metadata.

## 🚀 Features

- Categorize ingredients into known dishes
- Deployable for free via Hugging Face Spaces
- Lightweight and optimized for CPU inference

## 🛠️ Requirements

Make sure you have these in your `requirements.txt`:

```txt
gradio
transformers
torch
pillow
