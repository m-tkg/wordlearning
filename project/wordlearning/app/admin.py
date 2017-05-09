from django.contrib import admin
from app.models import Article
from app.models import WordCount
from app.models import Word

admin.site.register(Article)
admin.site.register(WordCount)
admin.site.register(Word)
