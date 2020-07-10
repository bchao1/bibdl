# -*- coding: UTF-8 -*-

"""
    Search from NIPS Proceedings: https://papers.nips.cc.
"""

from .utils import normalize
import requests
from bs4 import BeautifulSoup

class NIPSSearch:
    def __init__(self):
        self.base_url = 'https://papers.nips.cc'
        self.search_url =  'https://papers.nips.cc/search?q='
    
    def search(self, title):
        query = '+'.join(title.split(' '))
        res = requests.get(self.search_url + query)
        soup = BeautifulSoup(res.text, 'html.parser')
        papers = soup.findAll('li')
        entry = [p for p in papers if normalize(p.find('a').text.strip()) == normalize(title)]
        if not entry:
            return None
        entry_url = self.base_url + entry[0].find('a')['href']
        data = self.get_entry_data(entry_url)
        
        if not data:
            return None
        return self.gen_bib(data)

    def get_soup(self, url):
        return BeautifulSoup(requests.get(url).text, 'html.parser')

    def get_year(self, soup):
        year = soup.find('nav').findAll('li')[-1].text.strip()
        return year

    def get_title(self, soup):
        return soup.find('h2').text.strip()

    def get_authors(self, soup):
        authors = soup.find('ul', {'class': 'authors'}).findAll('li')
        authors = [a.text.strip() for a in authors]
        return authors

    def get_entry_data(self, url):
        try:
            soup = self.get_soup(url)
            title = self.get_title(soup)
            authors = self.get_authors(soup)
            year = self.get_year(soup)

            return {
                'title': title,
                'authors': authors,
                'conf': 'NeurIPS',
                'year': year
            }
        except:
            return None

    def gen_bib(self, data):
        tag = data['authors'][0].split(' ')[-1] + data['conf'] + data['year']
        conf_name = data['conf']
        bib = "@inproceedings{ " + tag + "\n" + \
              "    title = { " + data['title'] + " },\n" + \
              "    author = { " + ', '.join(data['authors']) + " },\n" + \
              "    booktitle = { " + conf_name + " },\n" + \
              "    year = { " + data['year'] + " }\n" + \
              "}"
        return bib


if __name__ == '__main__':
    nips = NIPSSearch()
    title = 'Domain Adaptation with Multiple Sources'
    bib = nips.search(title)
    print(bib)