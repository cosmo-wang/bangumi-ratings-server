from graphene import ObjectType, Field, InputObjectType, List, Date, String, Int, Float, Mutation
from graphene_django import DjangoObjectType
from django.db.models import Max
from bangumi_ratings_backend.models import Anime, SeasonAnime, SeasonRanking
from bangumi_ratings_backend.queries.queries import AnimeNode
import json
import datetime

class SeasonAnimeNode(DjangoObjectType):
  class Meta:
    model = SeasonAnime

class SeasonRankingNode(DjangoObjectType):
  class Meta:
    model = SeasonRanking

class UpdateOrAddAnimeInput(InputObjectType):
  anime_id = Int()
  name_zh = String()
  name_jp = String()
  cover_url = String()
  tv_episodes = Int()
  movies = Int()
  episode_length = Int()
  genre = String()
  year = String()
  douban_rating = Float()
  bangumi_tv_rating = Float()
  douban_link = String()
  bangumi_tv_link = String()
  description = String()
  season = String()
  release_date = String()
  broadcast_day = String()
  status = String()
  start_date = Date()
  end_date = Date()
  times_watched = Int()
  story = Float()
  illustration = Float()
  music = Float()
  passion = Float()

class UpdateOrAddSeasonAnimeInput(InputObjectType):
  anime_id = Int()
  name_zh = String()
  name_jp = String()
  season = String()
  release_date = Date()
  broadcast_day = String()
  status = String()
  genre = String()
  tv_episodes = Int()
  description = String()

class UpdateRankingsInput(InputObjectType):
  season = String(required=True)
  rankings = List(String)

class UpdateOrAddAnime(Mutation):
  class Arguments:
    new_data = UpdateOrAddAnimeInput(required=True)

  anime = Field(AnimeNode)

  def mutate(root, info, new_data):
    if not 'anime_id' in new_data:
      updated_anime, created = Anime.objects.update_or_create(
        name_zh=new_data.name_zh,
        defaults=new_data
      )
    else:
      updated_anime, created = Anime.objects.update_or_create(
        id=new_data.anime_id,
        defaults=new_data
      )
    return UpdateOrAddAnime(anime=updated_anime)

class UpdateOrAddSeasonAnime(Mutation):
  class Arguments:
    new_data = UpdateOrAddSeasonAnimeInput(required=True)

  anime = Field(AnimeNode)
  season_anime = Field(SeasonAnimeNode)
  season_ranking = Field(SeasonRankingNode)

  def mutate(root, info, new_data):
    anime_defaults = {}
    season_anime_defaults = {}
    for field_name, value in new_data.items():
      if field_name == 'season' and value:
        anime_defaults['year'] = value.split('年')[0]
      if field_name == 'release_date' and value:
        anime_defaults['year'] = value.year
        anime_defaults['start_date'] = value
      if field_name == 'season' or field_name == 'release_date' or field_name == 'broadcast_day':
        season_anime_defaults[field_name] = value
      else:
        anime_defaults[field_name] = value
    if not 'anime_id' in anime_defaults:
      updated_anime, anime_created = Anime.objects.update_or_create(
        name_zh=new_data.name_zh,
        defaults=anime_defaults
      )
    else:
      updated_anime, anime_created = Anime.objects.update_or_create(
        id=new_data.anime_id,
        defaults=anime_defaults
      )
    updated_season_anime, season_anime_created = SeasonAnime.objects.update_or_create(
      anime_id=updated_anime.id,
      defaults=season_anime_defaults
    )
    created_ranking = None
    if season_anime_created:
      new_ranking = SeasonRanking.objects.filter(season=new_data.season).values('anime_id').distinct().count() + 1
      created_ranking = SeasonRanking.objects.create(
        anime_id=updated_anime.id,
        season=new_data.season,
        date=datetime.datetime.today(),
        ranking=new_ranking
      )
    return UpdateOrAddSeasonAnime(anime=updated_anime, season_anime=updated_season_anime, season_ranking=created_ranking)

class UpdateRankings(Mutation):
  class Arguments:
    new_rankings = UpdateRankingsInput(required=True)

  season_rankings = List(SeasonRankingNode)

  def mutate(root, info, new_rankings):
    date = datetime.datetime.today()
    created_rankings = []
    for idx, name_zh in enumerate(new_rankings.rankings):
      anime_id = Anime.objects.get(name_zh=name_zh).id
      updated_ranking, created_ranking = SeasonRanking.objects.update_or_create(
        anime_id=anime_id,
        date=date,
        defaults={
          'season': new_rankings.season,
          'ranking': idx + 1
        }
      )
      created_rankings.append(updated_ranking)
    return UpdateRankings(season_rankings=created_rankings)

class DeleteAnime(Mutation):
  class Arguments:
    anime_id = Int()

  deleted_anime_name_zh = String()

  def mutate(root, info, anime_id):
    anime_to_delete = Anime.objects.get(id=anime_id)
    name_zh_to_delete = anime_to_delete.name_zh
    anime_to_delete.delete()
    return DeleteAnime(deleted_anime_name_zh=name_zh_to_delete)

class Mutation(ObjectType):
  update_or_add_anime = UpdateOrAddAnime.Field()
  update_or_add_season_anime = UpdateOrAddSeasonAnime.Field()
  update_rankings = UpdateRankings.Field()
  delete_anime = DeleteAnime.Field()
