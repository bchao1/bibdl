# -*- coding: UTF-8 -*-

"""
    Search from OpenReview.net.
    Need open review api.
"""

from .utils import normalize
import requests
from bs4 import BeautifulSoup
import openreview
import time

class OpenReviewSearch:
    def __init__(self, sess):
        self.base_url = 'https://openreview.net'
        self.api = openreview.Client(baseurl = self.base_url)
        self.sess = sess
    
    def search(self, title):
        query = '+'.join(title.split(' '))
        try:
            results = self.api.search_notes(term=query)
            if not results:
                return None
            try:
                results = [r for r in results if normalize(r.content['title']) == normalize(title) ]
            except:
                return None
            if not results:
                return None
            data = results[0].content
            time.sleep(0.1)
            return self.gen_bib(data)
        except Exception as e:
            return None
    
    def gen_bib(self, data):
        try:
            year = data['venue'].split(' ')[-1]
            conf = ' '.join(data['venue'].split(' ')[:-1])
            authors = data['authors']
            title = data['title']
            tag = authors[0].split(' ')[-1] + conf + year

            bib = "@inproceedings{ " + tag + "\n" + \
                "    title = { " + title + " },\n" + \
                "    author = { " + ', '.join(authors) + " },\n" + \
                "    booktitle = { " + conf + " },\n" + \
                "    year = { " + year + " }\n" + \
                "}"
            return bib
        except:
            return None

if __name__ == '__main__':
    op = OpenReviewSearch()
    title = 'Augmented Cyclic Adversarial Learning for Domain Adaptation'
    bib = op.search(title)
    print(bib)