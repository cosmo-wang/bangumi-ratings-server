from graphene import ObjectType, Field, InputObjectType, List, Date, String, Int, Float, Mutation
from graphene_django import DjangoObjectType
from django.db.models import Max
from bangumi_ratings_backend.models import Anime, SeasonRanking
from bangumi_ratings_backend.queries.queries import AnimeNode
import json
import datetime

class SeasonRankingNode(DjangoObjectType):
  class Meta:
    model = SeasonRanking

class UpdateOrAddAnimeInput(InputObjectType):
  id = Int()
  name_zh = String()
  name_jp = String()
  cover_url = String()
  tv_episodes = Int()
  episode_length = Int()
  genre = String()
  year = String()
  bangumi_tv_rating = Float()
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
  dmhy_search_terms = String()
  dmhy_tags = String()
  delayed_weeks = Int()

class UpdateRankingsInput(InputObjectType):
  season = String(required=True)
  rankings = List(String)

class UpdateAnime(Mutation):
  class Arguments:
    new_data = UpdateOrAddAnimeInput(required=True)

  anime = Field(AnimeNode)

  def mutate(root, info, new_data):
    print(new_data)
    updated_anime, created = Anime.objects.update_or_create(
      id=new_data.id,
      defaults=new_data
    )
    return UpdateAnime(anime=updated_anime)

class AddAnime(Mutation):
  class Arguments:
    new_data = UpdateOrAddAnimeInput(required=True)

  anime = Field(AnimeNode)

  def mutate(root, info, new_data):
    updated_anime = Anime.objects.create(**new_data)
    return AddAnime(anime=updated_anime)

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
    id = Int()

  deleted_anime_name_zh = String()

  def mutate(root, info, id):
    anime_to_delete = Anime.objects.get(id=id)
    name_zh_to_delete = anime_to_delete.name_zh
    anime_to_delete.delete()
    return DeleteAnime(deleted_anime_name_zh=name_zh_to_delete)

class Mutation(ObjectType):
  add_anime = AddAnime.Field()
  update_anime = UpdateAnime.Field()
  update_rankings = UpdateRankings.Field()
  delete_anime = DeleteAnime.Field()
