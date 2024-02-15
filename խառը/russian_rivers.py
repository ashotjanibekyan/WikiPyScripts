import re

import os.path
import pywikibot as pw
import requests
import mwparserfromhell

enwiki = pw.Site('en', 'wikipedia')
hywiki = pw.Site('hy', 'wikipedia')
ruwiki = pw.Site('ru', 'wikipedia')


def remove_wikilinks(wiki_text):
    wikicode = mwparserfromhell.parse(wiki_text)
    for link in wikicode.filter_wikilinks():
        if link.text:
            wikicode.replace(link, link.text)
        else:
            wikicode.replace(link, link.title)
    cleaned_text = str(wikicode)
    return cleaned_text

def remove_refs(wiki_text):
    wikicode = mwparserfromhell.parse(wiki_text)

    # Remove all ref tags and their content
    for tag in wikicode.filter_tags():
        if tag.tag == 'ref':
            wikicode.remove(tag)

    # Convert the modified wikicode back to text
    cleaned_text = str(wikicode)
    return cleaned_text


def convert_to_valid_filename(title):
    # Remove invalid characters
    valid_title = re.sub(r'[\\/:"*?<>|]', '', title)

    # Replace spaces with underscores
    valid_title = valid_title.replace(' ', '_')

    # Shorten length if needed (adjust the limit based on your requirements)
    max_length = 255  # Windows maximum path length
    if len(valid_title) > max_length:
        valid_title = valid_title[:max_length]

    return valid_title


r = requests.get('https://petscan.wmflabs.org/?psid=26927265&format=plain')
titles = r.text.split('\n')

# Assuming 'documents' is a list of your preprocessed documents
documents = []
ru_titles = []

for title in titles:
    path = f'../rivers/{convert_to_valid_filename(title)}.txt'
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            documents.append(f.read())
            ru_titles.append(title)
        continue
    continue
    page = pw.Page(ruwiki, title)

    parsed = mwparserfromhell.parse(page.text)

    templates = parsed.filter_templates()
    sections = parsed.get_sections()
    if len(sections) == 1:
        continue

    for template in templates:
        try:
            parsed.remove(template)
        except Exception as e:
            print(e)
    for section_index in range(len(sections)):
        headings = sections[section_index].filter_headings()
        if headings and headings[0].title.strip().lower() == 'примечания':
            for s in sections[section_index:]:
                parsed.remove(s)
            break
    else:
        continue
    document = remove_refs(str(parsed).strip())
    document = remove_wikilinks(str(document).strip())
    with open(path, 'w', encoding='utf-8') as f:
        f.write(document)
    documents.append(document)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)

tfidf_vectorizer = TfidfVectorizer()
optimal_k = 200
kmeans_optimal = KMeans(n_clusters=optimal_k, random_state=42)
pipeline_optimal = make_pipeline(tfidf_vectorizer, kmeans_optimal)
pipeline_optimal.fit(documents)

tfidf_matrix = tfidf_vectorizer.transform(documents)

clusters = pipeline_optimal.predict(documents)

centroids = np.zeros((optimal_k, tfidf_matrix.shape[1]))
for cluster_id in range(optimal_k):
    cluster_mask = (clusters == cluster_id)
    cluster_tfidf = tfidf_matrix[cluster_mask]
    centroids[cluster_id] = cluster_tfidf.mean(axis=0)

for doc_id, cluster_id in enumerate(clusters):
    print(f"Document {doc_id}: Cluster {cluster_id}")

average_similarities = []
for cluster_id in range(optimal_k):
    cluster_mask = (clusters == cluster_id)
    cluster_tfidf = tfidf_matrix[cluster_mask]

    # Calculate average cosine similarity
    similarity_matrix = cosine_similarity(cluster_tfidf, [centroids[cluster_id]])
    average_similarity = np.mean(similarity_matrix)
    average_similarities.append(average_similarity)

    # Print or use the average similarity as needed
    print(f"Cluster {cluster_id} Average Similarity: {average_similarity}")

    cluster_documents = [(documents[i], i) for i, c in enumerate(clusters) if c == cluster_id]
    cluster_filename = f"../rivers/result/similarity_{average_similarity:.4f}_{len(cluster_documents)}_cluster_{cluster_id}.txt"

    with open(cluster_filename, 'w', encoding='utf-8') as cluster_file:
        for doc in cluster_documents:
            cluster_file.write(f'\n\n----[[:ru:{ru_titles[doc[1]]}]]\n\n<pre>\n' + doc[0] + '\n</pre>')
