from flask import Flask
from pypdf import PdfReader


app = Flask(__name__)


@app.route("/")
def index():
    return "PDF"


@app.route("/read")
def read():
    reader = PdfReader("data/2022.pdf")
    number_of_pages = len(reader.pages)
    text_all = ""
    for i in range(0, number_of_pages):
        page = reader.pages[i]
        text = page.extract_text()
        text_all = text_all + text
    return {
        "pages": number_of_pages,
        "text": text_all,
    }


@app.route("/read/<int:page_number>")
def read_page_number(page_number):
    reader = PdfReader("data/2022.pdf")
    page = reader.pages[page_number - 1]
    text = page.extract_text()
    return {
        "page": page_number,
        "text": text,
    }