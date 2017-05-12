from django.db import models
from datetime import datetime


class WeblioLock(models.Model):
    status_list = (
        ('parsing', 'parsing'),
        ('complete', 'complete'),
        ('stop', 'stop')
    )
    status = models.CharField(verbose_name='Status', choices=status_list, max_length=16, default='parsing')
    create = models.DateTimeField(verbose_name='Create Date', default=datetime.now)
    update = models.DateTimeField(verbose_name='Update Date', auto_now=True)


class Article(models.Model):
    url = models.CharField(verbose_name='URL', max_length=255, unique=True)
    domain = models.CharField(verbose_name='Domain', max_length=255)
    date = models.DateField(verbose_name='Date')
    title = models.TextField(verbose_name='Title')
    body = models.TextField(verbose_name='Body')


class Word(models.Model):
    status_list = (
        ('master', 'success'),
        ('studying', 'info'),
        ('not started', 'danger'),
        ('ignore', 'default')
    )
    word = models.CharField(verbose_name='Word', max_length=255, unique=True)
    imageurl = models.CharField(verbose_name='ImageUrl', max_length=255, default='')
    meaning = models.CharField(verbose_name='Meaning', max_length=255, default='')
    status = models.CharField(verbose_name='Status', choices=status_list, max_length=16, default='not started')


class WordCount(models.Model):
    article_id = models.IntegerField(verbose_name='Article ID')
    word = models.ForeignKey(Word, related_name='word_of_WordCount')
    count = models.IntegerField(verbose_name='Count')


class Phrase(models.Model):
    phrase = models.CharField(verbose_name='Phrase', max_length=255, unique=True)
    meaning = models.CharField(verbose_name='Meaning', max_length=255)


class WordPhrase(models.Model):
    word = models.ForeignKey(Word, related_name='word_of_WordPhrase')
    phrase = models.ForeignKey(Phrase, related_name='phrase_of_WordPhrase')


class Example(models.Model):
    sentence = models.CharField(verbose_name='Sentence', max_length=255, unique=True)
    meaning = models.CharField(verbose_name='Meaning', max_length=255)


class WordExample(models.Model):
    word = models.ForeignKey(Word, related_name='word_of_WordExample')
    example = models.ForeignKey(Example, related_name='example_of_WordExample')
