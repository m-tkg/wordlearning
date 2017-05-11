# coding: utf-8
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime as dt
import re
from collections import Counter
from readability.readability import Document
from nltk.corpus import wordnet as wn


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
            word = wn.morphy(words[i])
            if word is None:
                word = ''
            words[i] = word

        counter = Counter(words)
        result = {}
        for word, count in counter.most_common():
            if len(word) >= 4:
                result[word] = count
        return result

    @staticmethod
    def weblioMeaning(url):
        htmlfp = urllib.request.urlopen(url)
        html = htmlfp.read().decode('utf-8', 'replace')
        htmlfp.close()
        s = BeautifulSoup(html, 'lxml')

        # meaning and image
        meaning = ''
        imageurl = ''
        meaningtag = s.find('td', class_='content-explanation')
        imagetag = s.find('div', class_='summaryM EGateCoreDataWrp')
        if meaningtag is not None:
            meaning = meaningtag.text
        if imagetag is not None and imagetag.find('img') is not None:
            imageurl = imagetag.find('img')['src']
        return(meaning, imageurl)

    @staticmethod
    def weblioWord(word):
        result = {}
        # word
        (meaning, imageurl) = Parse.weblioMeaning('http://ejje.weblio.jp/content/' + word)
        result['meaning'] = meaning
        result['imageurl'] = imageurl

        # phrase
        htmlfp = urllib.request.urlopen('http://ejje.weblio.jp/phrase/kenej/' + word)
        html = htmlfp.read().decode('utf-8', 'replace')
        htmlfp.close()
        s = BeautifulSoup(html, 'lxml')
        phrasetag = s.find('div', class_='phraseWords')
        phrases = []
        if phrasetag is not None:
            for phrase in phrasetag.findAll('a'):
                name = phrase.text
                (value, dummy) = Parse.weblioMeaning(phrase['href'])
                phrases.append({'text': name, 'meaning': value})
        result['phrases'] = phrases

        # example
        htmlfp = urllib.request.urlopen('http://ejje.weblio.jp/sentence/content/' + word)
        html = htmlfp.read().decode('utf-8', 'replace')
        htmlfp.close()
        s = BeautifulSoup(html, 'lxml')
        exampletag = s.findAll(class_='qotC')
        examples = []
        if exampletag is not None:
            for example in exampletag:
                try:
                    tag = example.find(class_='qotCE')
                    tag.find('span').extract()
                    tag.find('audio').extract()
                    tag.find('i').extract()
                    english = tag.text
                    tag = s.findAll(class_='qotC')[0].find(class_='qotCJ')
                    tag.find('span').extract()
                    japanese = tag.text
                    examples.append({'text': english, 'meaning': japanese})
                except:
                    pass
        result['examples'] = examples

        return result
