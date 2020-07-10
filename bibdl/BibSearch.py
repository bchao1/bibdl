# -*- coding: UTF-8 -*-
import concurrent.futures

from multiprocessing import Pool
from termcolor import colored
import sys
import collections
import time
import requests

from .search import ArxivSearch, \
                PapersWithCodeSearch, \
                NIPSSearch, \
                OpenReviewSearch

MAX_THREADS = 100

class BibSearch:
    def __init__(self, args):
        self.max_results = args.max_results
        self.engines = collections.OrderedDict()
        self.sess = requests.Session()

        # Make search engines
        self.engines['open-review'] = OpenReviewSearch(self.sess)
        if args.pwc:
            self.engines['papers-with-code'] = PapersWithCodeSearch(self.sess)
        if args.nips:
            self.engines['nips-web'] = NIPSSearch(self.sess)
        self.engines['arxiv'] = ArxivSearch(self.sess, self.max_results)

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
        for b in bibs:
            if b is not None:
                return b
        return None

    def search_single_seq(self, title):
        ''' Sequentially search, no multiprocesses. '''
        bibs = [e.search(title) for e in self.engines.values()]
        bib = self.choose_bib(bibs)
        self.show_bib_status(bib, title)
        #time.sleep(0.1)
        return bib

    def search_single(self, title):
        ''' Search for a single paper with threadpool. '''
        pool = Pool(processes = len(self.engines))
        results = [pool.map_async(e.search, [title]) for e in self.engines.values()]
        bibs = [r.get()[0] for r in results]
        pool.close()
        bib = self.choose_bib([bibs])
        self.show_bib_status(bib, title)
        return bib
    
    def write_bib_file(self, bibfile, result):
        with open(bibfile, 'a') as file:
            for title, bib in result:
                if bib is not None:
                    file.write('% ' + title + '\n')
                    file.write(bib + '\n\n')
        return 

    def write_unfound_files(self, result):
        with open('not_found.txt', 'a') as file:
            for title, bib in result:
                if bib is None:
                    file.write(title + '\n')
        return

    def search_from_file(self, filename, outbib):
        titles = self.read_titles_file(filename)
        return self.search_multiple(titles, outbib)

    def read_titles_file(self, filename):
        titles = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    title = line.strip()
                    if len(title) > 0:
                        titles.append(title)
            return titles
        except Exception as e:
            print(e)
            sys.exit(1)

    def search_multiple(self, titles, outbib):
        
        pool = Pool(processes = len(titles))
        result_bibs = pool.map_async(self.search_single_seq, titles)
        bibs = result_bibs.get()
        result = list(zip(titles, bibs))
        pool.close()
        self.show_search_status(bibs)
        self.write_bib_file(outbib, result)
        self.write_unfound_files(result)
        
        return result