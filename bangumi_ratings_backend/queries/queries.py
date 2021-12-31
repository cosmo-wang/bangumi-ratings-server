import graphene
from graphene_django import DjangoObjectType
from bangumi_ratings_backend.models import Anime, SeasonAnime, SeasonRanking, Quote
import datetime
import json

class AnimeNode(DjangoObjectType):
  class Meta:
    model = Anime
    fields = ('name_zh', 'name_jp', 'tv_episodes', \
              'movies', 'episode_length', 'status', 'genre', \
              'year', 'douban_rating', 'description', 'start_date', \
              'end_date', 'times_watched', 'story', 'illustration', \
              'music', 'passion')
  
  anime_id = graphene.Int()

  def resolve_anime_id(parent, info):
    return parent.id

class AnimeScheduleNode(DjangoObjectType):
  class Meta:
    model = SeasonAnime
    fields = ('season', 'release_date', 'broadcast_day')
  
  anime_id = graphene.Int()
  name_zh = graphene.String()
  name_jp = graphene.String()
  genre = graphene.String()
  tv_episodes = graphene.Int()
  status = graphene.String()
  description = graphene.String()
  rankings = graphene.JSONString(season=graphene.String())

  def resolve_name_zh(parent, info):
    return Anime.objects.get(id = parent.anime_id).name_zh

  def resolve_name_jp(parent, info):
    return Anime.objects.get(id = parent.anime_id).name_jp

  def resolve_genre(parent, info):
    return Anime.objects.get(id = parent.anime_id).genre

  def resolve_tv_episodes(parent, info):
    return Anime.objects.get(id = parent.anime_id).tv_episodes

  def resolve_status(parent, info):
    return Anime.objects.get(id = parent.anime_id).status
  
  def resolve_description(parent, info):
    return Anime.objects.get(id = parent.anime_id).description

  def resolve_rankings(parent, info):
    rankings_objs = SeasonRanking.objects.filter(
      anime_id = parent.anime_id,
      season = parent.season
    ).order_by('date')
    res_dict = {parent.season: {}}
    for r_obj in rankings_objs:
      res_dict[parent.season][r_obj.date.strftime('%Y-%m-%d')] = r_obj.ranking
    return json.dumps(res_dict, ensure_ascii=False)

class Query(graphene.ObjectType):
  get_animes = graphene.List(AnimeNode)
  get_season_schedules = graphene.List(AnimeScheduleNode)

  def resolve_get_animes(self, info, **kwargs):
    return Anime.objects.all().order_by('-end_date')

  def resolve_get_season_schedules(self, info):
    return SeasonAnime.objects.all().order_by('release_date')