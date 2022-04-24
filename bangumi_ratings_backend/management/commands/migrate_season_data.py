from django.core.management.base import BaseCommand
from bangumi_ratings_backend.models import Anime, SeasonAnime

def migrate_season_data():
  for season_anime in SeasonAnime.objects.all():
    Anime.objects.filter(id=season_anime.anime_id).update(season=season_anime.season, release_date=season_anime.release_date, broadcast_day=season_anime.broadcast_day)

class Command(BaseCommand):
  def handle(self, *args, **options):
    print("Start")
    migrate_season_data()
    print("Done")