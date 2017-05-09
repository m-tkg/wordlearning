# coding: utf-8
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime as dt
import re
from collections import Counter
from readability.readability import Document


class Parse:
    @staticmethod
    def getHtml(url):
        htmlfp = urllib.request.urlopen(url)
        html = htmlfp.read().decode('utf-8', 'replace')
        htmlfp.close()

        readable_article = BeautifulSoup(Document(html).summary().replace('</p>', '\n</p>'), 'lxml').getText()
        readable_title = Document(html).short_title()
        all_text = dt.now().strftime('%Y-%m-%d') + '\n' + readable_title + '\n' + readable_article
        all_text = re.sub(r'[\r\n]+', '\n', all_text, flags=re.MULTILINE)
        all_text = re.sub(r'[\t ]+', ' ', all_text)
        all_text = re.sub(r'^ ', '', all_text)
        all_text = re.sub(r' $', '', all_text)
        return all_text

    @staticmethod
    def countWord(text):
        text_simple = text.lower()
        text_simple = re.sub(r'[^a-z\'\-]', ' ', text_simple)
        words = re.split(r' ', text_simple)
        for i in range(len(words)):
            words[i] = re.sub(r'^\'', '', words[i])
            words[i] = re.sub(r'\'$', '', words[i])
            words[i] = re.sub(r'\'s$', '', words[i])
        counter = Counter(words)
        result = {}
        for word, count in counter.most_common():
            if len(word) >= 4:
                result[word] = count
        return result
