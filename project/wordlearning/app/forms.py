from django.forms import ModelForm
from app.models import Article


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ('url',)
