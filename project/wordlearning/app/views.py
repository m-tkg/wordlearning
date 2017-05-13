from django.shortcuts import redirect, render
from app.models import WeblioLock
from app.models import Article
from app.models import Word
from app.models import WordCount
from app.models import WordPhrase
from app.models import WordExample
from app.models import TestSequence
from app.lib.Parse import Parse
import urllib.parse
import threading
from django.db.models.aggregates import Sum
from django.db.models import Q
import random


def index(request):
    return redirect("app:articles")


def articles(request):
    articles = Article.objects.all().order_by('id').reverse()
    context = {'articles': articles, 'active_articles': True, 'template': './articles_list.html'}
    return render(request, './common/base.html', context)


def articlesView(request):
    if "id" not in request.GET:
        return redirect("app:articles")
    article = Article.objects.get(id=request.GET.get("id"))
    lines = article.body.split('\n')
    context = {
        'id': request.GET.get("id"),
        'title': article.title,
        'lines': lines,
        'active_articles': True,
        'template': './articles_view.html'
        }
    return render(request, './common/base.html', context)


def parseArticle(request):
    if "url" not in request.GET:
        return redirect("app:articles")

    url = request.GET.get("url")

    # article
    try:
        article = Article.objects.get(url=url)
    except:
        article = Article()
    text = Parse.getHtml(url)
    article.url = url
    article.domain = urllib.parse.urlparse(url).netloc
    (article.date, article.title, article.body) = text.split('\n', 2)
    article.body = article.body.strip()
    article.save()

    # word
    count = Parse.countWord(text)
    for w in count.keys():
        try:
            word = Word.objects.get(word=w)
        except:
            word = Word()
        try:
            wordcount = WordCount.objects.get(article_id=article.id, word=word.id)
        except:
            wordcount = WordCount()
        word.status = 'not started'
        word.word = w
        word.save()
        wordcount.article_id = article.id
        wordcount.word = word
        wordcount.count = count[w]
        wordcount.save()

    return redirect("app:articles")


def deleteArticle(request):
    if "id" not in request.GET:
        return redirect("app:articles")
    Article.objects.get(id=request.GET.get("id")).delete()
    WordCount.objects.filter(article_id=request.GET.get("id")).delete()
    return redirect("app:articles")


def words(request):
    if request.method == 'POST':
        status = request.POST.get('change_status')
        for id in request.POST.getlist('check'):
            word = Word.objects.get(id=id)
            word.status = status
            word.save()
        count_str = ''
        if "count" in request.POST:
            count_str = "?count=" + request.POST.get("count")
        return redirect(request.path + count_str)

    wordcount = WordCount.objects.values('word').annotate(cnt=Sum('count'))
    wordlist = Word.objects.all()
    count = 0
    if "count" in request.GET:
        count = int(request.GET.get("count"))
    words = []
    wordscnt = {}
    max = 0
    for w in wordcount:
        wordscnt[w['word']] = w['cnt']
    for w in wordlist:
        if w.id in wordscnt and wordscnt[w.id] >= count:
            word = {}
            word['id'] = w.id
            word['word'] = w.word
            word['meaning'] = w.meaning
            word['imageurl'] = w.imageurl
            word['cnt'] = wordscnt[w.id]
            word['status'] = w.status
            word['statuslabel'] = w.status.replace(' ', '_')
            words.append(word)
            if word['cnt'] > max:
                max = word['cnt']
    words = sorted(words, key=lambda x: x['cnt'], reverse=True)
    wordstatus = Word().status_list

    context = {
        'words': words,
        'wordstatus': wordstatus,
        'count': count,
        'max': max,
        'active_words': True,
        'template': 'words_list.html'
        }
    return render(request, './common/base.html', context)


def articleWords(request):
    if request.method == 'POST':
        status = request.POST.get('change_status')
        for id in request.POST.getlist('check'):
            word = Word.objects.get(id=id)
            word.status = status
            word.save()
        count_str = "?id=" + request.POST.get("id") + "&count=" + request.POST.get("count")
        return redirect(request.path + count_str)

    if "id" not in request.GET:
        return redirect("app:articles")
    wordcount = WordCount.objects.select_related().filter(article_id=request.GET.get("id"))
    count = 0
    if "count" in request.GET:
        count = int(request.GET.get("count"))
    words = []
    max = 0
    for w in wordcount:
        if w.count >= count:
            word = {}
            word['id'] = w.word.id
            word['word'] = w.word.word
            word['meaning'] = w.word.meaning
            word['imageurl'] = w.word.imageurl
            word['cnt'] = w.count
            word['status'] = w.word.status
            word['statuslabel'] = w.word.status.replace(' ', '_')
            words.append(word)
            if word['cnt'] > max:
                max = word['cnt']
    words = sorted(words, key=lambda x: x['cnt'], reverse=True)

    wordstatus = Word().status_list
    context = {
        'words': words,
        'wordstatus': wordstatus,
        'count': count,
        'id': request.GET.get("id"),
        'max': max,
        'active_words': True,
        'template': 'words_in_article.html'
        }
    return render(request, './common/base.html', context)


def wordsView(request):
    if "id" not in request.GET:
        return redirect("app:words")
    word = Word.objects.get(id=request.GET.get("id"))
    phrases = WordPhrase.objects.select_related().filter(word=word)
    examples = WordExample.objects.select_related().filter(word=word)
    context = {
        'word': word,
        'phrases': phrases,
        'examples': examples,
        'active_words': True,
        'template': './word_view.html'
        }
    return render(request, './common/base.html', context)


def weblio(request):
    try:
        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        if lock.status == 'parsing':
            return render(request, './ok.html')
        if lock.status == 'stop':
            return render(request, './ok.html')
    except:
        pass

    t = threading.Thread(target=Parse.weblio)
    t.start()

    return render(request, './ok.html')


def stopWeblio(request):
    try:
        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        if lock.status != 'stop':
            lock = WeblioLock()
            lock.status = 'stop'
            lock.save()
    except:
        pass

    return render(request, './ok.html')


def restartWeblio(request):
    try:
        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        if lock.status == 'stop':
            lock = WeblioLock()
            lock.status = 'restart'
            lock.save()
    except:
        pass

    return render(request, './ok.html')


def wordTest(request):
    wordstatus = Word().status_list
    if request.method == 'POST':
        _words = []
        for val in request.POST.getlist('status'):
            _words.append(wordstatus[int(val) - 1][0])
        if len(_words) == 1:
            queries = [Q(status=_words[0])]
        else:
            queries = [Q(status__contains=w) for w in _words]
        query = queries.pop()
        for item in queries:
            query |= item
        TestSequence.objects.all().delete()
        words = Word.objects.filter(query)
        words = sorted(words, key=lambda x: random.random())[:int(request.POST.get("max_questions"))]
        for word in words:
            test_seq = TestSequence()
            test_seq.word = word
            test_seq.save()
        return redirect(request.path + '?index=0')

    elif "index" not in request.GET:
        context = {
            'wordstatus': wordstatus,
            'active_test': True,
            'template': './test_start.html'
            }
        return render(request, './common/base.html', context)

    index = int(request.GET.get("index"))
    test_seqs = TestSequence.objects.select_related().all().order_by('id')
    # 2nd or later question answerd
    if index > 0:
        pre_question = test_seqs[index - 1]
        pre_question.answer = int(request.GET.get("answer"))
        pre_question.save()
    # all question answerd
    if index >= len(test_seqs):
        for question in test_seqs:
            if question.answer == 1:
                question.word.answer_ok += 1
            else:
                question.word.answer_ng += 1
            question.word.save()
        context = {
            'active_test': True,
            'template': './test_complete.html'
            }
        return render(request, './common/base.html', context)

    word = test_seqs[index].word
    phrases = WordPhrase.objects.select_related().filter(word=word)
    examples = WordExample.objects.select_related().filter(word=word)
    context = {
        'percentage': (index + 1) * 100 / len(test_seqs),
        'next_index': index + 1,
        'word': word,
        'phrases': phrases,
        'examples': examples,
        'active_test': True,
        'template': './test.html'
        }
    return render(request, './common/base.html', context)


def phraseTest(request):
    wordstatus = Word().status_list
    if request.method == 'POST':
        _words = []
        for val in request.POST.getlist('status'):
            _words.append(wordstatus[int(val) - 1][0])
        if len(_words) == 1:
            queries = [Q(status=_words[0])]
        else:
            queries = [Q(status__contains=w) for w in _words]
        query = queries.pop()
        for item in queries:
            query |= item
        TestSequence.objects.all().delete()
        words = Word.objects.filter(query)
        words = sorted(words, key=lambda x: random.random())[:int(request.POST.get("max_questions"))]
        for word in words:
            test_seq = TestSequence()
            test_seq.word = word
            test_seq.save()
        return redirect(request.path + '?index=0')

    elif "index" not in request.GET:
        context = {
            'wordstatus': wordstatus,
            'active_test': True,
            'template': './test_start.html'
            }
        return render(request, './common/base.html', context)

    index = int(request.GET.get("index"))
    test_seqs = TestSequence.objects.select_related().all().order_by('id')
    # 2nd or later question answerd
    if index > 0:
        pre_question = test_seqs[index - 1]
        pre_question.answer = int(request.GET.get("answer"))
        pre_question.save()
    # all question answerd
    if index >= len(test_seqs):
        for question in test_seqs:
            if question.answer == 1:
                question.word.answer_ok += 1
            else:
                question.word.answer_ng += 1
            question.word.save()
        context = {
            'active_test': True,
            'template': './test_complete.html'
            }
        return render(request, './common/base.html', context)

    word = test_seqs[index].word
    phrases = WordPhrase.objects.select_related().filter(word=word)
    examples = WordExample.objects.select_related().filter(word=word)
    context = {
        'percentage': (index + 1) * 100 / len(test_seqs),
        'next_index': index + 1,
        'word': word,
        'phrases': phrases,
        'examples': examples,
        'active_test': True,
        'template': './test.html'
        }
    return render(request, './common/base.html', context)
