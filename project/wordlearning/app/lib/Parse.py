# coding: utf-8
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime as dt
import re
from collections import Counter
from readability.readability import Document
from nltk.corpus import wordnet as wn
from app.models import WeblioLock
from app.models import Word
from app.models import WordPhrase
from app.models import Phrase
from app.models import Example
from app.models import WordExample
from app.lib.Common import Common


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
                if len(phrases) >= 10:
                    break
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
                    tag = example.find(class_='qotCJ')
                    tag.find('span').extract()
                    japanese = tag.text
                    if len(english) < 256 and len(japanese) < 256:
                        examples.append({'text': english, 'meaning': japanese})
                        if len(examples) >= 10:
                            break
                except:
                    pass
        result['examples'] = examples

        return result

    @staticmethod
    def _checkStop():
        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        return (lock.status == 'stop')

    @staticmethod
    def weblio():
        words = Word.objects.filter(meaning='')
        if len(words) == 0:
            return

        lock = WeblioLock()
        lock.save()

        for word in words:
            if Parse._checkStop():
                break
            result = Parse.weblioWord(word.word)
            word.meaning = result['meaning']
            word.imageurl = result['imageurl']
            word.save()
            if word.meaning == '':
                Common.changeStatus(word=word, status='Ignore')
            for phrase in result['phrases']:
                try:
                    Phrase.objects.get(phrase=phrase['text'])
                except:
                    new_phrase = Phrase()
                    new_phrase.phrase = phrase['text']
                    new_phrase.meaning = phrase['meaning']
                    new_phrase.save()
                    Common.changeStatus(phrase=new_phrase)
                    if new_phrase.meaning == '':
                        Common.changeStatus(phrase=new_phrase, status='ignore')

                    wordphrase = WordPhrase()
                    wordphrase.word = word
                    wordphrase.phrase = new_phrase
                    wordphrase.save()
            for example in result['examples']:
                try:
                    Example.objects.get(sentence=example['text'])
                except:
                    new_example = Example()
                    new_example.sentence = example['text']
                    new_example.meaning = example['meaning']
                    new_example.save()
                    wordexample = WordExample()
                    wordexample.word = word
                    wordexample.example = new_example
                    wordexample.save()

        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        if lock.status == 'parsing':
            lock.status = 'complete'
            lock.save()
