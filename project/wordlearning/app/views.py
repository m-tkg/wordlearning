from django.shortcuts import redirect, render
from app.models import Article
from app.models import Word
from app.models import WordCount
from app.forms import ArticleForm
from app.lib.Parse import Parse
import urllib.parse
from django.db.models.aggregates import Sum


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
            word['word'] = w.word
            word['cnt'] = wordscnt[w.id]
            word['status'] = w.status
            words.append(word)
            if word['cnt'] > max:
                max = word['cnt']
    words = sorted(words, key=lambda x: x['cnt'], reverse=True)

    context = {'words': words, 'count': count, 'max': max, 'active_words': True, 'template': 'words_list.html'}
    return render(request, './common/base.html', context)


def words_view(request):
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
            word['word'] = w.word.word
            word['cnt'] = w.count
            word['status'] = w.word.status
            words.append(word)
            if word['cnt'] > max:
                max = word['cnt']
    words = sorted(words, key=lambda x: x['cnt'], reverse=True)

    context = {'words': words, 'count': count, 'id': request.GET.get("id"), 'max': max, 'active_wordsinarticle': True, 'template': 'words_in_article.html'}
    return render(request, './common/base.html', context)
