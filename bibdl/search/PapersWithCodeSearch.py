# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
from .utils import normalize

class PapersWithCodeSearch:
    def __init__(self, sess):
        self.base_url = 'https://paperswithcode.com'
        self.search_url = "https://paperswithcode.com/search?q="
        self.sess = sess
    
    def get_soup(self, url):
        return BeautifulSoup(self.sess.get(url).text, 'html.parser')

    def get_title(self, soup):
        return soup.find('h1').text.strip()

    def search(self, title):
        q = '+'.join(list(map(str.strip, title.split(' '))))
        soup = self.get_soup(self.search_url + q)
        entries = soup.findAll('div', {'class': ['item']})
        entry = [e for e in entries if normalize(self.get_title(e)) == normalize(title)]
        if not entry:
            return None
        entry_url = self.base_url + entry[0].find('h1').find('a')['href']
        data = self.get_entry_data(entry_url)
        if not data:
            return None
        return self.gen_bib(data)
    
    def get_entry_data(self, url):
        try:
            soup = self.get_soup(url).find('div', {'class': 'paper-title'})
            conf_data = soup.find('span', {'class': 'item-conference-link'}).text
            conf, year = tuple(map(str.strip, conf_data.split(' ')))
            author_spans = soup.findAll('span', {'class': 'author-span'})
            authors = [span.text.strip() for span in author_spans]
            if authors[-1].split(' ')[0] == 'and':
                authors[-1] = ' '.join(authors[-1].split(' ')[1:])
            return {
                'title': soup.find('h1').text,
                'conf': conf,
                'year': year.strip(),
                'authors': authors
            }
        except:
            return None
    
    def gen_bib(self, data):
        tag = data['authors'][0].split(' ')[-1] + data['year']
        conf_name = data['conf']
        bib = "@inproceedings{ " + tag + "\n" + \
              "    title = { " + data['title'] + " },\n" + \
              "    author = { " + ', '.join(data['authors']) + " },\n" + \
              "    booktitle = { " + conf_name + " },\n" + \
              "    year = { " + data['year'] + " }\n" + \
              "}"
        return bib