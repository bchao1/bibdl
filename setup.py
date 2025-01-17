from setuptools import setup, find_namespace_packages

setup(
    name = 'bibdl',
    author = "Mckinsey666",
    description = "BibTeX style references for ML/DL.",
    version = '0.1.0',
    packages = ['bibdl', 'bibdl/search'],
    url = "https://github.com/Mckinsey666/bibdl",
    keywords = "ml dl referece bibtex tex",
    install_requires = [
        'termcolor',
        'feedparser',
        'beautifulsoup4',
        'openreview-py',
    ],
    entry_points = {
        'console_scripts': [
            'bibdl = bibdl.__main__:main'
        ]
    })