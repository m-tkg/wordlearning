from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^articles$', views.articles_list, name='articles_list'),
    url(r'^view/article$', views.articles_view, name='articles_view'),
    url(r'^parse/article$', views.articles_parse, name='articles_parse'),
    url(r'^delete/article$', views.articles_delete, name='articles_delete'),
    url(r'^words$', views.words_list, name='words_list'),
    url(r'^view/words$', views.words_view, name='words_view'),
    url(r'^parse/weblio$', views.weblio, name='weblio'),
]
