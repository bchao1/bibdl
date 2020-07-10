from argparse import ArgumentParser
from . import BibSearch
import time

def main():
    parser = ArgumentParser()
    parser.add_argument('-t', '--title', type = str, nargs = '+', help = "Title of paper to search.")
    parser.add_argument('--max_results', type = int, default = 1000, help = "Mex return results for arXiv API.")
    parser.add_argument('-l', '--list', type = str, default = './list.txt', help = "Paper list to search.")
    parser.add_argument('--bib', type = str, default = './refs.bib', help = "Output reference .bib file.")

    parser.add_argument('--pwc', action = 'store_true', help = "Use Papers With Code Search.")
    parser.add_argument('--nips', action = 'store_true', help = "Use NIPS open access search.")
    
    args = parser.parse_args()

    if args.title is not None and args.list is not None:
        print("Choose to search by paper list or by single title.")
    elif args.title is None and args.list is None:
        print("Specify to search by paper list or by single title.")
    else:
        bibsearch = BibSearch(args)
        start = time.time()
        if args.title:
            bib = bibsearch.search_single(' '.join(args.title))
        elif args.list:
            bibs = bibsearch.search_from_file(args.list, args.bib)
        time_spent = time.time() - start
        print("Time elapsed: {}s".format(time_spent))

if __name__ == '__main__':
    main()