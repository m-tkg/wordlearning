from django.db import models


class Article(models.Model):
    url = models.CharField(verbose_name='URL', max_length=255, unique=True)
    domain = models.CharField(verbose_name='Domain', max_length=255)
    date = models.DateField(verbose_name='Date')
    title = models.TextField(verbose_name='Title')
    body = models.TextField(verbose_name='Body')


class Word(models.Model):
    status_list = (
        ('master', 'master'),
        ('studying', 'studying'),
        ('not started', 'not started'),
        ('ignore', 'ignore')
    )
    word = models.CharField(verbose_name='Word', max_length=255, unique=True)
    status = models.CharField(verbose_name='Status', choices=status_list, max_length=16)


class WordCount(models.Model):
    article_id = models.IntegerField(verbose_name='Article ID')
    # word = models.CharField(verbose_name='Word', max_length=255)
    word = models.ForeignKey(Word, related_name='p_word')
    count = models.IntegerField(verbose_name='Count')
