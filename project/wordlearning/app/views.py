from django.shortcuts import redirect, render
from app.models import Article
from app.models import Word
from app.models import WordCount
from app.models import WordPhrase
from app.models import Phrase
from app.models import Example
from app.models import WordExample
from app.forms import ArticleForm
from app.lib.Parse import Parse
import urllib.parse
from django.db.models.aggregates import Sum


def index(request):
    return redirect("app:articles_list")


def articles_list(request):
    articles = Article.objects.all().order_by('id')
    form = ArticleForm(instance=Article())
    context = {'form': form, 'articles': articles, 'active_articles': True, 'template': './articles_list.html'}
    return render(request, './common/base.html', context)


def articles_view(request):
    if "id" not in request.GET:
        return redirect("app:articles_list")
    article = Article.objects.get(id=request.GET.get("id"))
    lines = article.body.split('\n')
    context = {'lines': lines, 'active_articles': True, 'template': './articles_view.html'}
    return render(request, './common/base.html', context)


def articles_parse(request):
    if request.method == 'POST':
        if "url" in request.POST:
            url = request.POST.get("url")

            # article
            try:
                article = Article.objects.get(url=url)
            except:
                article = Article()
            text = Parse.getHtml(url)
            article.url = url
            article.domain = urllib.parse.urlparse(url).netloc
            (article.date, article.title, article.body) = text.split('\n', 2)
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

    return redirect("app:articles_list")


def articles_delete(request):
    if "id" not in request.GET:
        return redirect("app:articles_list")
    Article.objects.get(id=request.GET.get("id")).delete()
    WordCount.objects.filter(article_id=request.GET.get("id")).delete()
    return redirect("app:articles_list")


def words_list(request):
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
            word['cnt'] = wordscnt[w.id]
            word['status'] = w.status
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


def words_view(request):
    if request.method == 'POST':
        status = request.POST.get('change_status')
        for id in request.POST.getlist('check'):
            word = Word.objects.get(id=id)
            word.status = status
            word.save()
        count_str = "?id=" + request.POST.get("id") + "&count=" + request.POST.get("count")
        return redirect(request.path + count_str)

    if "id" not in request.GET:
        return redirect("app:articles_list")
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
            word['cnt'] = w.count
            word['status'] = w.word.status
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
        'active_wordsinarticle': True,
        'template': 'words_in_article.html'
        }
    return render(request, './common/base.html', context)


def weblio(request):
    words = Word.objects.filter(meaning='')
    for word in words:
        result = Parse.weblioWord(word.word)
        word.meaning = result['meaning']
        word.imageurl = result['imageurl']
        word.save()
        for phrase in result['phrases']:
            try:
                Phrase.objects.get(phrase=phrase['text'])
            except:
                new_phrase = Phrase()
                new_phrase.phrase = phrase['text']
                new_phrase.meaning = phrase['meaning']
                new_phrase.save()
                wordphrase = WordPhrase()
                wordphrase.word = word
                wordphrase.phrase = new_phrase
                wordphrase.save()
        for example in result['examples']:
            try:
                Example.objects.get(phrase=example['text'])
            except:
                new_example = Example()
                new_example.sentence = example['text']
                new_example.meaning = example['meaning']
                new_example.save()
                wordexample = WordExample()
                wordexample.word = word
                wordexample.example = new_example
                wordexample.save()
    return render(request, './ok.html')
