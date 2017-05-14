from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^article/list$', views.articleList, name='article_list'),
    url(r'^article/view$', views.articleView, name='article_view'),
    url(r'^word/list$', views.wordphrasesList, name='word_list'),
    url(r'^word/view$', views.wordphraseView, name='word_view'),
    url(r'^word/test$', views.wordphraseTest, name='word_test'),
    url(r'^phrase/list$', views.wordphrasesList, name='phrase_list'),
    url(r'^phrase/view$', views.wordphraseView, name='phrase_view'),
    url(r'^phrase/test$', views.wordphraseTest, name='phrase_test'),

    url(r'^delete/article$', views.deleteArticle, name='delete_article'),
    url(r'^parse/article$', views.parseArticle, name='parse_article'),
    url(r'^parse/weblio$', views.weblio, name='weblio'),
    url(r'^stop/weblio$', views.stopWeblio, name='stop_weblio'),
    url(r'^resume/weblio$', views.resumeWeblio, name='resume_weblio'),
]
