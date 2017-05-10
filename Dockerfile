FROM python:3.6.1
RUN pip install beautifulsoup4 lxml django mysqlclient readability-lxml nltk; python -c 'import nltk; nltk.download("wordnet")'
