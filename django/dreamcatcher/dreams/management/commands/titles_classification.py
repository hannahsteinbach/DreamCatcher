from django.core.management.base import BaseCommand
import random
from django.apps import apps


class Command(BaseCommand):
    help = 'Update titles and classifications for all dreams (randomly)'

    def handle(self, *args, **kwargs):
        Dream = apps.get_model('dreams', 'Dream')

        dreams = Dream.objects.filter(user__username='vickie')

        for dream in dreams:
            dream.title = dream.optional_titles[0] # just choose the first of the proposed titles
            dream.classification = ''              # get no classified dream instead of None

            dream.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated types of dream and titles for vickies dreams'))


# how to run? -> like this: in django/dreamcatcher/python manage.py titles_classification