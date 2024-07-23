import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcatcher.settings')
django.setup()


from dreams.models import Dream
from dreams.utils import add_dream_to_collection

dreams = Dream.objects.all()

for dream in dreams:
    add_dream_to_collection(dream.id, dream.content)

print("Created embeddings for all dreams and added them to the collection.")
