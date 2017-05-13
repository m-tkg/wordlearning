from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^articles$', views.articles, name='articles'),
    url(r'^articles/view$', views.articlesView, name='articles_view'),
    url(r'^word/list$', views.wordphrasesList, name='words'),
    url(r'^phrase/list$', views.wordphrasesList, name='phrases'),
    url(r'^words/view$', views.wordsView, name='words_view'),
    url(r'^word/test$', views.wordphraseTest, name='word_test'),
    url(r'^phrase/test$', views.wordphraseTest, name='phrase_test'),

    url(r'^delete/article$', views.deleteArticle, name='delete_article'),
    url(r'^parse/article$', views.parseArticle, name='parse_article'),
    url(r'^parse/weblio$', views.weblio, name='weblio'),
    url(r'^stop/weblio$', views.stopWeblio, name='stop_weblio'),
    url(r'^restart/weblio$', views.restartWeblio, name='restart_weblio'),
]
