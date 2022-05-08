from django.core.management.base import BaseCommand
from bangumi_ratings_backend.models import Anime, AnimeRating, SeasonAnime, SeasonRanking
import json
import datetime

def import_animes():
  with open('/bangumi-ratings-server/bangumi_ratings_backend/data/Ratings.json') as f:
    data = json.load(f)["results"]
    for anime_data in data:
      print(anime_data["name"])
      start_date = anime_data.get("start_date", '').split('-')
      if len(start_date) == 3:
        start_date = datetime.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
      else:
        start_date = None
      end_date = anime_data.get("end_date", '').split('-')
      if len(end_date) == 3:
        end_date = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
      else:
        end_date = None
      print(start_date, end_date)
      obj, created = Anime.objects.update_or_create(
        name_zh = anime_data["name"],
        tv_episodes = anime_data.get("tv_episodes", 0),
        movies = anime_data.get("movies", 0),
        episode_length = anime_data.get("episode_length", 0),
        status = anime_data["status"],
        genre = anime_data["genre"],
        year = anime_data.get("year", ""),
        douban_rating = anime_data.get("douban", 0.0),
        description = anime_data.get("description", ""),
        start_date = start_date,
        end_date = end_date,
        times_watched = anime_data.get("times_watched", 0)
      )
      print(obj)
    
def import_ratings():
  with open('/bangumi-ratings-server/bangumi_ratings_backend/data/Ratings.json') as f:
    data = json.load(f)["results"]
    for anime_data in data:
      print(anime_data["name"])
      anime_id = Anime.objects.get(name_zh=anime_data["name"]).id
      _, created = AnimeRating.objects.get_or_create(
        anime_id = anime_id,
        story = anime_data["story"],
        illustration = anime_data["illustration"],
        music = anime_data["music"],
        passion = anime_data["passion"]
      )
      print(created)

def import_new_animes():
  with open('/bangumi-ratings-server/bangumi_ratings_backend/data/NewAnimes.json') as f:
    data = json.load(f)["results"]
    for anime_data in data:
      anime, created = Anime.objects.get_or_create(
        name_zh = anime_data["name"],
        defaults = {
          "tv_episodes": anime_data["tv_episodes"],
          "genre": anime_data["genre"],
          "description": anime_data["description"],
          "status": anime_data["status"],
        }
      )
      if not created:
        anime_id = anime.id
        print(f"Found: {anime.name_zh}")
      else:
        print(f"Created: {anime.name_zh}")
      seasons = anime_data["season"].split("，")
      for season in seasons:
        _, created = SeasonAnime.objects.get_or_create(
          anime = anime_id,
          season = season,
          release_date = None if anime_data.get("start_date", "") == "" else anime_data.get("start_date", ""),
          broadcast_day = anime_data.get("next_episode_day", ""),
        )
      
def import_rankings():
  with open('/bangumi-ratings-server/bangumi_ratings_backend/data/NewAnimes.json') as f:
    data = json.load(f)["results"]
    for anime_data in data:
      print(anime_data["name"])
      anime_id = Anime.objects.get(name_zh=anime_data["name"]).id
      seasons_ranking = anime_data["seasons_ranking"]
      for season, rankings in seasons_ranking.items():
        for date, ranking in rankings.items():
          SeasonRanking.objects.get_or_create(
            anime_id = anime_id,
            season = season,
            ranking = ranking,
            date = datetime.datetime.fromisoformat(date),
          )

def cleanup_ratings():
  for rating_obj in AnimeRating.objects.all():
    anime = Anime.objects.get(id=rating_obj.anime_id)
    if anime.status == "在看" or anime.status == "想看":
      rating_obj.delete()

def migrate_ratings():
  for rating_obj in AnimeRating.objects.all():
    Anime.objects.filter(id=rating_obj.anime_id).update(story=rating_obj.story, illustration=rating_obj.illustration, music=rating_obj.music, passion=rating_obj.passion)

class Command(BaseCommand):

  def handle(self, *args, **options):
    print("Start")
    migrate_ratings()
    print("Done")