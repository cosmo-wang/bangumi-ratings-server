from django.core.management.base import BaseCommand
from bangumi_ratings_backend.models import Anime

def fill_search_term_with_name_zh():
  for anime in Anime.objects.all():
    dmhy_search_terms = anime.dmhy_search_terms
    if (dmhy_search_terms == ''):
      Anime.objects.filter(id=anime.id).update(dmhy_search_terms=anime.name_zh)
    elif (anime.name_zh not in dmhy_search_terms):
      Anime.objects.filter(id=anime.id).update(dmhy_search_terms=anime.dmhy_search_terms + ',' + anime.name_zh)

class Command(BaseCommand):
  def handle(self, *args, **options):
    print("Start")
    fill_search_term_with_name_zh()
    print("Done")