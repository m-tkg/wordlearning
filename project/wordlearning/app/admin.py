from django.contrib import admin
from app.models import Article
from app.models import WordCount
from app.models import Word
from app.models import WordPhrase
from app.models import Phrase
from app.models import Example

admin.site.register(Article)
admin.site.register(WordCount)
admin.site.register(Word)
admin.site.register(WordPhrase)
admin.site.register(Phrase)
admin.site.register(Example)
