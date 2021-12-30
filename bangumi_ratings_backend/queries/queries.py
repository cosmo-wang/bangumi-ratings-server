import graphene
from graphene_django import DjangoObjectType
from bangumi_ratings_backend.models import Anime, AnimeRating, SeasonAnimes, SeasonRanking, Quote
import datetime
import json

class RatedAnimeNode(DjangoObjectType):
  class Meta:
    model = Anime
    fields = ('id', 'name_zh', 'name_jp', 'tv_episodes', 'movies', 'episode_length', 'status', 'genre', 'year', 'douban_rating', 'description', 'start_date', 'end_date', 'times_watched')
  
  id = graphene.Int()
  story = graphene.Float()
  illustration = graphene.Float()
  music = graphene.Float()
  passion = graphene.Float()

  def resolve_story(parent, info):
    return AnimeRating.objects.get(anime_id = parent.id).story

  def resolve_illustration(parent, info):
    return AnimeRating.objects.get(anime_id = parent.id).illustration

  def resolve_music(parent, info):
    return AnimeRating.objects.get(anime_id = parent.id).music

  def resolve_passion(parent, info):
    return AnimeRating.objects.get(anime_id = parent.id).passion

class UnratedAnimeNode(DjangoObjectType):
  class Meta:
    model = Anime
    fields = ('id', 'name_zh', 'name_jp', 'tv_episodes', 'movies', 'episode_length', 'status', 'genre', 'year', 'douban_rating', 'description', 'start_date')
    
  id = graphene.Int()

class AnimeScheduleNode(DjangoObjectType):
  class Meta:
    model = SeasonAnimes
    fields = ('season', 'release_date', 'broadcast_day')
  
  name_zh = graphene.String()
  genre = graphene.String()
  tv_episodes = graphene.Int()
  status = graphene.String()
  rankings = graphene.JSONString(season=graphene.String())

  def resolve_name_zh(parent, info):
    return Anime.objects.get(id = parent.anime_id).name_zh

  def resolve_genre(parent, info):
    return Anime.objects.get(id = parent.anime_id).genre

  def resolve_tv_episodes(parent, info):
    return Anime.objects.get(id = parent.anime_id).tv_episodes

  def resolve_status(parent, info):
    return Anime.objects.get(id = parent.anime_id).status

  def resolve_rankings(parent, info):
    rankings_objs = SeasonRanking.objects.filter(
      anime_id = parent.anime_id,
      season = parent.season
    ).order_by('date')
    res_dict = {parent.season: {}}
    for r_obj in rankings_objs:
      res_dict[parent.season][r_obj.date.strftime('%Y-%m-%d')] = r_obj.ranking
    return json.dumps(res_dict)

class Query(graphene.ObjectType):
  get_watched_animes = graphene.List(RatedAnimeNode)
  get_watching_animes = graphene.List(UnratedAnimeNode)
  get_to_watch_animes = graphene.List(UnratedAnimeNode)
  get_season_schedules = graphene.List(AnimeScheduleNode, season=graphene.String())

  def resolve_get_watched_animes(self, info, **kwargs):
    return Anime.objects.filter(status='已看').order_by('-end_date')

  def resolve_get_watching_animes(self, info, **kwargs):
    return Anime.objects.filter(status='在看').order_by('-start_date')

  def resolve_get_to_watch_animes(self, info, **kwargs):
    return Anime.objects.filter(status='想看')

  def resolve_get_season_schedules(self, info, season):
    return SeasonAnimes.objects.filter(season=season).order_by('release_date')