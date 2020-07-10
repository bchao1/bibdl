# -*- coding: UTF-8 -*-
import feedparser
import time
from .utils import normalize

class ArxivSearch:
    def __init__(self, sess, max_results):
        self.max_results = max_results
        self.search_url = 'http://export.arxiv.org/api/query?' + \
                          'search_query=all:{}&' + \
                          'start=0&' + \
                          'max_results=' + str(self.max_results)
        self.sess = sess
    
    def get_xml_feed(self, url):
        return feedparser.parse(self.sess.get(url).text)

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
        time.sleep(0.1)
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