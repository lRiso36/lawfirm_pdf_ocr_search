# OCR PDF Search (Law Firm Workflow Tool)

A Streamlit app that OCR-scans scanned PDFs (e.g., police reports / discovery PDFs) and enables fast keyword search with page-level results and context snippets.

## Why this exists
Built to reduce manual search time in large scanned case files. Implemented in a small law-firm workflow and packaged into a Windows EXE so non-technical users can run it.

## How it works
- Renders each PDF page to an image using PyMuPDF
- Runs OCR with Tesseract
- Stores text by page in memory
- Searches and displays matched pages with context snippets

## Run locally
1. Install Python 3.10+  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
