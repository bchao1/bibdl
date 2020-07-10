# -*- coding: UTF-8 -*-

"""
    Search from CVF Open Access.
    Papers are from CVPR, ICCV 2013~
    No ECCV Papers
"""

from utils import normalize
import requests
from bs4 import BeautifulSoup

class CVFSearch:
    def __init__(self):
        self.base_url = 'https://openaccess.thecvf.com/menu'
        self.confs = self.parse_conference_url(self.base_url)
        self.workshop_conf = [url for url in self.confs if 'workshops' in url]
        self.main_conf = [url for url in self.confs if 'workshops' not in url]
        print(self.main_conf)

    def parse_conference_url(self, url):
        soup = self.get_soup(self.base_url)
        confs = soup.find('div', {'id': 'content'}).find('dl').findAll('a')
        return [self.base_url + '/' + a['href'] for a in confs]

    def get_soup(self, url):
        return BeautifulSoup(requests.get(url).text, 'html.parser')

if __name__ == '__main__':
    cvf = CVFSearch()