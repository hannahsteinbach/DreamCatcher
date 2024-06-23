from django.core.management.base import BaseCommand
from django.apps import apps
from keybert import KeyBERT


class Command(BaseCommand):
    help = 'Update keywords for all existing dreams'

    def handle(self, *args, **kwargs):
        kw_model = KeyBERT()

        Dream = apps.get_model('dreams', 'Dream')

        dreams = Dream.objects.all()

        for dream in dreams:
            content_str = str(dream.content)
            keywords = kw_model.extract_keywords(content_str, keyphrase_ngram_range=(1, 1), stop_words=None)
            dream.keywords = [keyword[0] for keyword in keywords]
            dream.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated keywords for all dreams'))



# how to run? -> like this: in django/dreamcatcher/python manage.py keywords_olderdreams