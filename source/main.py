import PyPDF2
from tkinter import *
import threading
import re
import os
import sys
import time
import metapy
import pytoml as toml
#import pdfplumber
import fitz



def extract_textbook():
    pdf_path = textbook_path.get()
    extract_and_save_text(pdf_path, 'text_data')



#this works!!!!
def extract_and_save_text(pdf_path, output_dir):
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                with open(os.path.join(output_dir, f'doc_{page_num}.txt'), 'w') as out_file:
                    out_file.write(text)



## The attempt below was a bit better but still is not parsing the pages correctly.

# def correct_spacing(text):
#     # Simple heuristic: add a space before each capital letter
#     corrected_text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
#     return corrected_text

# def extract_and_save_text(pdf_path, output_dir):
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf.pages):
#             text = page.extract_text()
#             if text:
#                 # Apply the spacing correction
#                 corrected_text = correct_spacing(text)
#                 with open(os.path.join(output_dir, f'doc_{page_num}.txt'), 'w') as out_file:
#                     out_file.write(corrected_text)

## ------------------------

## Below was the earlier attempt which was not working well.

# def extract_and_save_text(pdf_path, output_dir):
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf.pages):
#             text = page.extract_text()
#             if text:  # Check if text is extracted
#                 with open(os.path.join(output_dir, f'doc_{page_num}.txt'), 'w') as out_file:
#                     out_file.write(text)


## Below is the first attempt which does not work at all.
# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfFileReader(file)
#         return [reader.getPage(page_num).extractText() for page_num in range(reader.numPages)]

def build_index(config_file):
    idx = metapy.index.make_inverted_index(config_file)
    return idx

def search_metapy(idx, query_str):
    ranker = metapy.index.OkapiBM25()
    query = metapy.index.Document()
    query.content(query_str)
    top_docs = ranker.score(idx, query, num_results=5)
    return [(idx.metadata(doc_id).get('content'), score) for doc_id, score in top_docs]

def perform_search():
    query = query_string.get()
    # Assuming the text has already been extracted and saved in 'text_data'
    idx = build_index('config.toml')
    results = search_metapy(idx, query)

    # Update the GUI with results
    loading_label.config(text="Search Completed")
    for result in results:
        print(result)

def search_result():
    threading.Thread(target=perform_search).start()
    loading_label.config(text="Searching...")

def load_subtitle():
    subtitle_path_value = subtitle_path.get()
    with open(subtitle_path_value, 'r') as file:
        subtitle_content = file.read()
    return subtitle_content

def parse_subtitle(subtitle_content):
    # Basic parsing for .srt files
    pattern = re.compile(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.*?)\n\n', re.DOTALL)
    subtitles = pattern.findall(subtitle_content)
    return " ".join(subtitles)


def search_result():
    # Start the search in a new thread
    threading.Thread(target=perform_search).start()

    # Update GUI to show loading animation/message
    loading_label.config(text="Searching...")


    # Display results (this part can be enhanced to show more details)


window = Tk()
window.title("CS410 Final Project")
window.config( padx=20, pady=20)

canvas = Canvas(width=300, height=300)
canvas.grid(column=1,row=0)
textbook_label = Label(text="Enter Textbook Path: ")
textbook_path = Entry(width=39)
textbook_path.focus()
textbook_path.insert(0,"/Users/jaecho/Desktop/SourceCode/cs410/project/resource/TextDataManagementandAnalysis.pdf")

textbook_load_button = Button(text="Load TextBook", command=extract_textbook, width=14)
textbook_label.grid(column=0, row=1)
textbook_path.grid(column=1, columnspan=2, row=1)
textbook_load_button.grid(column=3,row=1)

subtitle_label = Label(text="Enter Subtitle Path: ")
subtitle_path = Entry(width=39)
subtitle_path.focus()
subtitle_path.insert(0,"/Users/jaecho/Desktop/SourceCode/cs410/project/resource/Lesson 1.3_ Text Retrieval Problem.vtt")
subtitle_load_button = Button(text="Load Subtitle", command=load_subtitle, width=14)
subtitle_label.grid(column=0, row=2)
subtitle_path.grid(column=1, columnspan=2, row=2)
subtitle_load_button.grid(column=3,row=2)

query_label = Label(text="Enter the search query: ")
query_string = Entry(width=39)
query_string.focus()
query_string_button = Button(text="Search", command=search_result, width=14)
query_label.grid(column=0, row=3)
query_string.grid(column=1, columnspan=2, row=3)
query_string_button.grid(column=3,row=3)


loading_label = Label(text="Status")
loading_label.grid(column=1, row=4)

window.mainloop()
