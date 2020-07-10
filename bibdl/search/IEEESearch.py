# -*- coding: UTF-8 -*-

"""
    Search from IEEE Xplore.
"""

from utils import normalize
import requests
from bs4 import BeautifulSoup
from credentials import KEYS
import xplore

class IEEESearch:
    def __init__(self):
        self.key = KEYS['IEEEXplore']
        self.api = xplore.xploreapi.XPLORE(self.key)
    
    def search(self, title):
        self.api.articleTitle(title)
        data = self.api.callAPI()
        print(data)

if __name__ == '__main__':
    ieee = IEEESearch()
    title = 'Comparison of deep transfer learning strategies for digital pathology'
    ieee.search(title)
