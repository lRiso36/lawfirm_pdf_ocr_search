# ALL IMPORTS
import streamlit as st
import fitz
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed  # ADD THIS
import re
import os
import sys

# static variable
ZOOM = 400 / 72


# portable path logic
def getResourcePath(relativePath):
    """Finds Tesseract folder whether app is running
    as a python script or a bundled exe"""

    try:
        # path only exists inside EXE
        basePath = sys._MEIPASS
    except Exception:
        # if fails, run as normal script
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)


# path to tesseract engine
tessPath = getResourcePath(r"Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tessPath


# scanning one page function
def ocr_page(page_data):
    """worker function that handles one single page"""

    pageNum, page, mat = page_data

    # convert pdf to image
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert(
        "L"
    )  # 'L' is grayscale for speed

    # run OCR engine on image
    text = pytesseract.image_to_string(img)

    # return dicitonary with page number and content
    return {"page": pageNum + 1, "content": text.lower()}


# document processing


def processPDF(uploadedFile):
    """
    manages the "Turbo" scanning
    splits the PDF into pages and hands them out to multiple threads
    """

    # open pdf doc
    document = fitz.open(stream=uploadedFile.read(), filetype="pdf")
    totalPages = len(document)
    mat = fitz.Matrix(ZOOM, ZOOM)

    # Setup streamlit progress bar
    statusText = st.empty()
    progressBar = st.progress(0)
    statusText.text(f"Document loaded. Preparing to scan {totalPages} total pages...")

    database = []

    # runs multiple ocr_page() at once
    with ThreadPoolExecutor() as executor:
        future_to_page = {
            executor.submit(ocr_page, (i, document.load_page(i), mat)): i
            for i in range(totalPages)
        }

        # update progress bar after each page finishes
        completedCount = 0
        for future in as_completed(future_to_page):
            result = future.result()
            database.append(result)

            completedCount += 1
            percent = completedCount / totalPages
            progressBar.progress(percent)
            statusText.text(f" Scanning: Page {completedCount} of {totalPages}...")

    # sort results
    database = sorted(database, key=lambda x: x["page"])

    document.close()
    statusText.text(" Document Ready! ")
    return database


# run main interface


def main():
    st.title(" PDF Search ")

    # file uploader
    uploadedFile = st.file_uploader("Upload a scanned PDF", type="pdf")

    if uploadedFile:
        fileID = uploadedFile.name

        # Session State: Only run the scan IF it's a new file.
        if "last_file" not in st.session_state or st.session_state.last_file != fileID:
            st.session_state.db = processPDF(uploadedFile)
            st.session_state.last_file = fileID

        # search bar
        query = st.text_input("Search for a word or name in this document: ")

        if query:
            query = query.lower().strip()
            searchResults = []

            # loop through database we created
            for entry in st.session_state.db:
                if query in entry["content"]:
                    start = entry["content"].find(query)
                    contextStart = max(0, start - 100)
                    contextEnd = min(len(entry["content"]), start + len(query) + 100)
                    snippet = entry["content"][contextStart:contextEnd].replace(
                        "\n", " "
                    )

                    # add results to lists
                    searchResults.append(
                        {
                            "Page": f"Page {entry['page']}",
                            "Preview": f"...{snippet}...",
                            "Full Text": entry["content"],  # kept hidden
                        }
                    )
            # display search results
            if searchResults:
                st.success(f"Found {len(searchResults)} occurences")

                for r in searchResults:
                    with st.container(border=True):
                        # use columns to keep page seperate from text
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown(f"**{r['Page']}**")
                        with col2:
                            # highlight search term
                            highlighted = r["Preview"].replace(
                                query, f":red[**{query.upper()}**]"
                            )
                            st.write(highlighted)
            else:
                st.warning(f"No results found for {query}")


if __name__ == "__main__":
    main()
