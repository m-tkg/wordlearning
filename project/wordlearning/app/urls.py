from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^articles$', views.articles, name='articles'),
    url(r'^articles/view$', views.articlesView, name='articles_view'),
    url(r'^articles/words$', views.articleWords, name='article_words'),
    url(r'^words$', views.words, name='words'),
    url(r'^words/view$', views.wordsView, name='words_view'),

    url(r'^delete/article$', views.deleteArticle, name='delete_article'),
    url(r'^parse/article$', views.parseArticle, name='parse_article'),
    url(r'^parse/weblio$', views.weblio, name='weblio'),
]
