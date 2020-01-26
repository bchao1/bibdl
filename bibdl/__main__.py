from argparse import ArgumentParser
from .Search import BibSearch

def main():
    parser = ArgumentParser()
    parser.add_argument('-t', '--title', type = str, nargs = '+', help = "Title of paper.")
    parser.add_argument('--max_results', type = int, default = 10000)
    parser.add_argument('-l', '--list', type = str, default = './list.txt')
    parser.add_argument('--bib', type = str, default = './refs.bib')
    args = parser.parse_args()

    if args.title is not None and args.list is not None:
        print("Choose to search by paper list or by single title.")
    elif args.title is None and args.list is None:
        print("Specify to search by paper list or by single title.")
    else:
        bibsearch = BibSearch(args.max_results)
        if args.title:
            bib = bibsearch.search_single(' '.join(args.title))
        elif args.list:
            bibs = bibsearch.search_from_file(args.list, args.bib)

if __name__ == '__main__':
    main()