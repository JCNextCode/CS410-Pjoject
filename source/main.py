from tkinter import *
import os
import sys
import metapy
import pytoml as toml
import fitz
import json
from collections import Counter

def extract_textbook():
    pdf_path = textbook_path.get()
    extract_and_save_text(pdf_path, 'text_data')

def extract_and_save_text(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data_file_path = os.path.join(output_dir, 'text_data.dat')
    loading_label.config(text="Load Complete")
    with fitz.open(pdf_path) as doc, open(data_file_path, 'w') as data_file:
        metadata = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                # Write text to data file, one page per line
                data_file.write(text.replace('\n', ' ') + '\n')
                # Collect metadata for each page
                metadata.append({'id': page_num, 'content': text[:50]})  # Example metadata

        # Write metadata to file
        #json.dump(metadata, meta_file)




def perform_search():
    queries = load_subtitle()
    cfg = 'config.toml'
    idx = metapy.index.make_inverted_index(cfg)

    print('Number of documents : {0}'.format(int(idx.num_docs())))
    print('Number of unique terms {0}: '.format(int(idx.unique_terms())))
    print('Average document length {0}: '.format(float(idx.avg_doc_length())))
    print('Total corpus terms : {0}'.format(int(idx.total_corpus_terms())))

    #ranker = metapy.index.OkapiBM25()
    ranker =  metapy.index.OkapiBM25(k1=1.9, b=0.79)
    #ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = toml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    top_k = 5

    # query_path = query_cfg.get('query-path', 'subtitle-queries.txt')
    # query_start = query_cfg.get('query-id-start', 0)

    print('Running queries')

    ranked_doc_ids = []
    for query_text in queries:
        query = metapy.index.Document()
        query.content(query_text.strip())
        #print(f"Running queries on {query}")
        results = ranker.score(idx, query, top_k)
        print('\r Result : {}'.format(results))
        #print(f"Results for query: '{query_text}'")
        for num, (d_id, _) in enumerate(results):
            content = idx.metadata(d_id).get('content')
            #print('\r Content : {}'.format())
            # print('\r Rank : {}'.format(num + 1))
            # print('\r DocID: {}'.format(d_id))
            # print('\r - {}'.format(content))
            ranked_doc_ids.append(int(d_id))

    counter = Counter(ranked_doc_ids)
    top_page_list = counter.most_common(10)
    print(top_page_list)

    canvas.delete("all")
    start_y = 10  # Starting y position for the first text item
    y_increment = 20  # Increment in y position for each subsequent text item
    for i, (page, count) in enumerate(top_page_list):
        #text = "Page {0} appeared {1} times and is highly relevant to the lecture video.".format(page, count)
        text = "Page {0} highly relevant to the lecture video.".format(page, count)
        canvas.create_text(10, start_y + i * y_increment, anchor='nw', text=text, width=500)

def search_result():
    # Start the search in a new thread
    #threading.Thread(target=perform_search).start()
    perform_search()
    # Update GUI to show loading animation/message
    loading_label.config(text="Search Complete")
    # Display results (this part can be enhanced to show more details)

def load_subtitle():
    subtitle_path_value = subtitle_path.get()
    with open(subtitle_path_value, 'r') as file:
        subtitle_lines = file.readlines()
    queries = [line.strip() for line in subtitle_lines]
    loading_label.config(text="Load Complete")
    return queries



window = Tk()
window.title("CS410 Final Project")
window.config( padx=20, pady=20)

canvas = Canvas(width=300, height=300)
canvas.grid(column=1,row=0)
textbook_label = Label(text="Enter Textbook Path: ")
textbook_path = Entry(width=39)
#textbook_path.focus()
textbook_path.insert(0,"./input/TextDataManagementandAnalysis.pdf")

textbook_load_button = Button(text="Load TextBook ", command=extract_textbook, width=14)
textbook_label.grid(column=0, row=1)
textbook_path.grid(column=1, columnspan=2, row=1)
textbook_load_button.grid(column=3,row=1)

subtitle_label = Label(text="Load Lecture Video Subtitle ")
subtitle_path = Entry(width=39)
#subtitle_path.focus()
subtitle_path.insert(0,"./input/12.7 Contextual Text Mining_ Mining Causal Topics with Time Series Supervision.txt")
subtitle_load_button = Button(text="Load Subtitle", command=load_subtitle, width=14)
subtitle_label.grid(column=0, row=2)
subtitle_path.grid(column=1, columnspan=2, row=2)
subtitle_load_button.grid(column=3,row=2)

# query_label = Label(text="Enter the search query: ")
# query_string = Entry(width=39)
# query_string.focus()
query_string_button = Button(text="Search Pages", command=search_result, width=14)
#query_label.grid(column=0, row=3)
#query_string.grid(column=1, columnspan=3, row=3)
query_string_button.grid(column=3,row=3)


loading_label = Label(text="Status")
loading_label.grid(column=1, row=4)

window.mainloop()
