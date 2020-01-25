import requests
import feedparser
import pprint
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from multiprocessing import Pool
import time

# in entries: id, links, summary, authors, title, published_parsed, tags

def match(source, target):
    return fuzz.ratio(source.lower(), target.lower())

def get_authors_list(authors):
    return [a.name for a in authors]

def get_pdf_link(links):
    for l in links:
        if l.type == 'application/pdf':
            return l.href
    return None

def get_abstract_link(links):
    for l in links:
        if l.type == 'text/html':
            return l.href
    return None

def prune_title(title):
    return ' '.join(list(map(str.strip, title.split('\n'))))

def prune_arxiv_entry(entry):
    return {
        'id': entry.id,
        'title': prune_title(entry.title),
        'abs': get_abstract_link(entry.links),
        'pdf': get_pdf_link(entry.links),
        'authors': get_authors_list(entry.authors),
        'year': str(entry.published_parsed.tm_year),
        'summary': ' '.join(entry.summary.split('\n')),
        'tag': "" if len(entry.tags) == 0 else entry.tags[0].term
    }

def get_arxiv_entries(params):
    title, max_results = params
    url = 'http://export.arxiv.org/api/query?search_query=all:{}&start=0&max_results={}'.format(title, max_results)
    res = requests.get(url)
    entries = list(map(prune_arxiv_entry, feedparser.parse(res.text).entries))
    entries = sorted(
        entries, 
        reverse = True, 
        key = lambda x: match(x['title'], title)
    )
    return entries

def find_title(soup):
    return soup.find('h1').text.strip()

def find_conf(soup):
    conf =  soup.find('span', {'class': 'item-conference-link'})
    conf = "" if conf is None else conf.text.strip()
    return conf

def get_title_conf(soup):
    return {'title': find_title(soup), 'conf': find_conf(soup)}

def get_conf_entries(title):
    q = '+'.join(title.split(' '))
    url = "https://paperswithcode.com/search?q="
    res = requests.get(url + q)
    soup = BeautifulSoup(res.text, 'html.parser')
    entries = soup.findAll('div', {'class': ['item']})
    entries = list(map(get_title_conf, entries))
    entries = sorted(
        entries, 
        reverse = True, 
        key = lambda x: match(x['title'], title)
    )
    return entries

def gen_arxiv_bib(data):
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

def gen_conf_bib(data, conf):
    tag = data['authors'][0].split(' ')[-1] + data['year']
    conf_name = conf.split(' ')[0]
    bib = "@inproceedings{ " + tag + "\n" + \
          "    title = { " + data['title'] + " },\n" + \
          "    author = { " + ', '.join(data['authors']) + " },\n" + \
          "    booktitle = { " + conf_name + " },\n" + \
          "    year = { " + data['year'] + " }\n" + \
          "}"
    return bib

max_results = 100
title = str(input("Enter title => "))


pool = Pool(processes = 2)
result_arxiv = pool.map_async(get_arxiv_entries, [(title, max_results)])
result_conf = pool.map_async(get_conf_entries, [title])

entries = result_arxiv.get()[0]
confs = result_conf.get()[0]
for e in entries:
    print(e['title'])
print("---")
for e in confs:
    print(e['title'])

print(gen_conf_bib(entries[0], confs[0]['conf']))
print(gen_arxiv_bib(entries[0]))
