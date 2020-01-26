# bibdl
> Automatically generate BibTeX style references for ml/dl papers.

## Installation
> Build locally. You can easily customize the code.
```
git clone https://github.com/Mckinsey666/bibdl.git
cd bibdl
python3 -m pip install .
```

## Usage
```
bibdl --list list.txt --bib refs.bib
```
List all paper titles in `list.txt`. `bibdl` will spawn multiple processes to search for the papers on arXiv and paperswithcode.com and generate BibTeX style references in `refs.bib`. 
   
Papers that are not found will be listed in `not_found.txt`. You'll have to manually find references for those papers.

## Disclaimer
This is not expected to be a search engine, so make sure you get your paper titles right (or you might not be able to find anything). I simply hate looking for which conference a paper is submitted to, manually copying references, and finally formatting them, so let the computer do their work. 
   
If you get most of your paper titles right, usually the script finds 70% or more papers in the list. 

## Sources
- arXiv
- Papers with Code

## TODO
- Add dblp support (but dblp's API works badly...)
