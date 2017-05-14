from django.shortcuts import redirect, render
from app.models import WeblioLock
from app.models import Article
from app.models import Word
from app.models import Phrase
from app.models import WordCount
from app.models import WordPhrase
from app.models import WordExample
from app.models import TestSequence
from app.models import AnswerHistory
from app.lib.Parse import Parse
from app.lib.Common import Common
import urllib.parse
import threading
from django.db.models.aggregates import Sum
from django.db.models import Q
import random


def index(request):
    return redirect("app:article_list")


def articleList(request):
    articles = Article.objects.all().order_by('id').reverse()
    context = {'articles': articles, 'active_article': True, 'template': './articles_list.html'}
    return render(request, './common/base.html', context)


def articleView(request):
    if "id" not in request.GET:
        return redirect("app:article_list")
    article = Article.objects.get(id=request.GET.get("id"))
    lines = article.body.split('\n')
    context = {
        'id': request.GET.get("id"),
        'title': article.title,
        'lines': lines,
        'active_article': True,
        'template': './articles_view.html'
        }
    return render(request, './common/base.html', context)


def parseArticle(request):
    if "url" not in request.GET:
        return redirect("app:article_list")

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
        Common.changeStatus(word=word)
        wordcount.article_id = article.id
        wordcount.word = word
        wordcount.count = count[w]
        wordcount.save()

    return redirect("app:article_list")


def deleteArticle(request):
    if "id" not in request.GET:
        return redirect("app:article_list")
    Article.objects.get(id=request.GET.get("id")).delete()
    WordCount.objects.filter(article_id=request.GET.get("id")).delete()
    return redirect("app:article_list")


def wordphrasesList(request):
    mode = request.path.split('/')[1]

    article_id = 0
    title = ''
    if "id" in request.GET:
        article_id = int(request.GET.get("id"))
    elif "id" in request.POST:
        article_id = int(request.POST.get("id"))

    if article_id != 0:
        article = Article.objects.get(id=article_id)
        title = article.title

    if request.method == 'POST':
        status = request.POST.get('change_status')
        if mode == 'word':
            for id in request.POST.getlist('check'):
                word = Word.objects.get(id=id)
                Common.changeStatus(word=word, status=status)
        else:
            for id in request.POST.getlist('check'):
                phrase = Phrase.objects.get(id=id)
                Common.changeStatus(word=phrase, status=status)
        params = ''
        if article_id != 0:
            params = "?id=" + str(article_id)
        return redirect(request.path + params)

    if mode == 'word':
        targetlist = Word.objects.all()
        if article_id == 0:
            wordcount = WordCount.objects.all().values('word').annotate(cnt=Sum('count'))
        else:
            wordcount = WordCount.objects.filter(article_id=article_id).values('word').annotate(cnt=Sum('count'))
        wordscnt = {}
        for w in wordcount:
            wordscnt[w['word']] = w['cnt']
    else:
        if article_id == 0:
            targetlist = Phrase.objects.all()
        else:
            wordcount = WordCount.objects.filter(article_id=article_id)
            queries = [Q(word_id=w.word_id) for w in wordcount]
            query = queries.pop()
            for item in queries:
                query |= item
            _phrases = WordPhrase.objects.filter(query)
            queries = [Q(id=p.phrase.id) for p in _phrases]
            query = queries.pop()
            for item in queries:
                query |= item
            targetlist = Phrase.objects.filter(query)

    targets = []
    for t in targetlist:
        if mode == 'word' and t.id not in wordscnt:
            continue
        target = {}
        target['id'] = t.id
        if mode == 'word':
            target['word'] = t.word
            target['imageurl'] = t.imageurl
            target['cnt'] = wordscnt[t.id]
        else:
            target['word'] = t.phrase
        target['meaning'] = t.meaning
        target['status'] = t.status
        target['statuslabel'] = t.status.replace(' ', '_')
        targets.append(target)
    if mode == 'word':
        targets = sorted(targets, key=lambda x: x['cnt'], reverse=True)
    wordstatus = Word().status_list

    context = {
        'mode': mode,
        'words': targets,
        'wordstatus': wordstatus,
        'article_id': article_id,
        'title': title,
        'active_' + mode + '_list': True,
        'template': 'wordphrase_list.html'
        }
    return render(request, './common/base.html', context)


def wordView(request):
    if "id" not in request.GET:
        return redirect("app:word")
    word = Word.objects.get(id=request.GET.get("id"))
    phrases = WordPhrase.objects.select_related().filter(word=word)
    examples = WordExample.objects.select_related().filter(word=word)
    context = {
        'title': word.word,
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


def resumeWeblio(request):
    try:
        lock = WeblioLock.objects.order_by('id').reverse()[:1][0]
        if lock.status == 'stop':
            lock = WeblioLock()
            lock.status = 'restart'
            lock.save()
    except:
        pass

    return render(request, './ok.html')


def wordphraseTest(request):
    mode = request.path.split('/')[1]
    status = Word().status_list
    # create tests
    if request.method == 'POST':
        _targets = []
        for val in request.POST.getlist('status'):
            _targets.append(status[int(val) - 1][0])
        if len(_targets) == 1:
            queries = [Q(status=_targets[0])]
        else:
            queries = [Q(status=t) for t in _targets]
        query = queries.pop()
        for item in queries:
            query |= item
        TestSequence.objects.all().delete()
        if mode == 'word':
            targets = Word.objects.filter(query)
        else:
            targets = Phrase.objects.filter(query)
        targets = sorted(targets, key=lambda x: random.random())[:int(request.POST.get("max_questions"))]
        for target in targets:
            test_seq = TestSequence()
            if mode == 'word':
                test_seq.word = target
            else:
                test_seq.phrase = target
            test_seq.save()
        return redirect(request.path + '?index=0')

    # test settings
    elif "index" not in request.GET:
        context = {
            'wordstatus': status,
            'mode': mode,
            'active_' + mode + 'test': True,
            'template': './test_start.html'
            }
        return render(request, './common/base.html', context)

    # answering
    index = int(request.GET.get("index"))
    test_seqs = TestSequence.objects.select_related().all().order_by('id')
    # 2nd or later question answerd
    if index > 0:
        pre_question = test_seqs[index - 1]
        pre_question.answer = int(request.GET.get("answer"))
        pre_question.save()
        answer_history = AnswerHistory()
        if mode == 'word':
            answer_history.word = pre_question.word
        else:
            answer_history.word = pre_question.phrase
        answer_history.type = mode
        answer_history.answer = pre_question.answer
        answer_history.save()
    # all question answerd
    if index >= len(test_seqs):
        context = {
            'mode': mode,
            'active_' + mode + 'test': True,
            'template': './test_complete.html'
            }
        return render(request, './common/base.html', context)

    word = test_seqs[index].word
    phrase = test_seqs[index].phrase
    examples = WordExample.objects.select_related().filter(word=word)
    if mode == 'word':
        title = word.word
        phrases = WordPhrase.objects.select_related().filter(word=word)
    else:
        title = phrase.phrase
        phrases = WordPhrase.objects.select_related().filter(phrase=phrase)
    context = {
        'percentage': (index + 1) * 100 / len(test_seqs),
        'next_index': index + 1,
        'test': True,
        'title': title,
        'word': word,
        'phrases': phrases,
        'examples': examples,
        'mode': mode,
        'active_' + mode + 'test': True,
        'template': './word_view.html'
        }
    return render(request, './common/base.html', context)
