# -*- coding: UTF-8 -*-

import requests
import feedparser
from bs4 import BeautifulSoup
from multiprocessing import Pool
from termcolor import colored
from .utils import normalize

class ArxivSearch:
    def __init__(self, max_results):
        self.max_results = max_results
        self.search_url = 'http://export.arxiv.org/api/query?' + \
                          'search_query=all:{}&' + \
                          'sortBy=relevance&' + \
                          'start=0&' + \
                          'max_results=' + str(self.max_results)
    
    def get_xml_feed(self, url):
        return feedparser.parse(requests.get(url).text)

    def get_authors(self, authors):
        return [a.name for a in authors]

    def get_pdf_link(self, links):
        for l in links:
            if l.type == 'application/pdf':
                return l.href
        return None

    def get_abstract_link(self, links):
        for l in links:
            if l.type == 'text/html':
                return l.href
        return None

    def get_title(self, title):
        return ' '.join(list(map(str.strip, title.split('\n'))))

    def get_entry_data(self, entry):
        try:
            return {
                'id': entry.id,
                'title': self.get_title(entry.title),
                'abs': self.get_abstract_link(entry.links),
                'pdf': self.get_pdf_link(entry.links),
                'authors': self.get_authors(entry.authors),
                'year': str(entry.published_parsed.tm_year),
                'summary': ' '.join(entry.summary.split('\n')),
                'tag': "" if len(entry.tags) == 0 else entry.tags[0].term
            }
        except:
            return None

    def search(self, title):
        entries = self.get_xml_feed(self.search_url.format(title)).entries
        entry = [e for e in entries if normalize(self.get_title(e.title)) == normalize(title)]
        if not entry:
            return None
        data = self.get_entry_data(entry[0])
        if not data:
            return None
        return self.gen_bib(data)
    
    def gen_bib(self, data):
        eprint = data['id'].split('/')[-1]
        tag = data['authors'][0].split(' ')[-1] + data['year']
        bib = "@misc{ " + tag + "\n" + \
              "    title = { " + data['title'] + " },\n" + \
              "    author = { " + ', '.join(data['authors']) + " },\n" + \
              "    eprint = { " + eprint + " },\n" + \
              "    archivePrefix = { arXiv },\n" + \
              "    year = { " + data['year'] + " }\n" + \
              "}"
        return bib


class PapersWithCodeSearch:
    def __init__(self):
        self.base_url = 'https://paperswithcode.com'
        self.search_url = "https://paperswithcode.com/search?q="
    
    def get_soup(self, url):
        return BeautifulSoup(requests.get(url).text, 'html.parser')

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
    

def search_from_file(filename, max_results):
    titles = []
    with open(filename, 'r') as file:
        for line in file:
            titles.append(line.strip())
    pool = Pool(processes = len(titles))
    results = pool.map_async(get_entries, [(t, max_results) for t in titles])
    return results.get()

class BibSearch:
    def __init__(self, max_results):
        self.max_results = max_results
        self.ArxivSearch = ArxivSearch(max_results)
        self.PapersWithCodeSearch = PapersWithCodeSearch()

    def show_search_status(self, results):
        found = len(results) - results.count(None)
        rate = 100 * (1 - results.count(None) / len(results))
        print(colored(str(rate) + '%', 'green', attrs = ['bold']) + \
              ' ({}/{})'.format(found, len(results)) + ' papers found')

    def show_bib_status(self, bib, title):
        if bib:
            print('[' + colored('✓', 'green', attrs = ['bold']) + ']  ' + title)
        else:
            print('[' + colored('✗', 'red', attrs = ['bold']) + ']  ' + title)

    def choose_bib(self, bibs):
        bib = None
        for b in bibs[::-1]:
            if b is not None:
                bib = b
        return bib

    def search_single_seq(self, title):
        ''' Sequentially search, no multiprocesses. '''
        arxiv_bib = self.ArxivSearch.search(title)
        paperswithcode_bib = self.PapersWithCodeSearch.search(title)
        bib = self.choose_bib([paperswithcode_bib, arxiv_bib])
        self.show_bib_status(bib, title)
        return bib

    def search_single(self, title):
        ''' Search for a single paper with threadpool. '''
        pool = Pool(processes = 2)
        result_arxiv = pool.map_async(self.ArxivSearch.search, [title])
        result_paperswithcode = pool.map_async(self.PapersWithCodeSearch.search, [title])
        arxiv_bib = result_arxiv.get()[0]
        paperswithcode_bib = result_paperswithcode.get()[0]
        bib = self.choose_bib([paperswithcode_bib, arxiv_bib])
        self.show_bib_status(bib, title)
        return bib
    
    def write_bib_file(self, bibfile, result):
        with open(bibfile, 'w') as file:
            for title, bib in result:
                if bib is not None:
                    file.write('% ' + title + '\n')
                    file.write(bib + '\n\n')
        return 

    def write_unfound_files(self, result):
        with open('not_found.txt', 'w') as file:
            for title, bib in result:
                if bib is None:
                    file.write(title + '\n')
        return

    def search_from_file(self, filename, outbib):
        return self.search_multiple(self.read_titles_file(filename), outbib)

    def read_titles_file(self, filename):
        titles = []
        with open(filename, 'r') as file:
            for line in file:
                titles.append(line.strip())
        return titles

    def search_multiple(self, titles, outbib):
        pool = Pool(processes = len(titles))
        result_bibs = pool.map_async(self.search_single_seq, titles)
        bibs = result_bibs.get()
        result = list(zip(titles, bibs))
        self.show_search_status(bibs)
        self.write_bib_file(outbib, result)
        self.write_unfound_files(result)
        return result