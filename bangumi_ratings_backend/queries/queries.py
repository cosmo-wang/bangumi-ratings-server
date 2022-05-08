from graphene import Field, ObjectType, List, String, Int, Float, JSONString
from graphene_django import DjangoObjectType
from bangumi_ratings_backend.models import Anime, SeasonRanking
from bangumi_ratings_backend.utils.scrape_data import *
import json

class AnimeNode(DjangoObjectType):
  class Meta:
    model = Anime
    fields = ('name_zh', 'name_jp', 'cover_url', 'tv_episodes', \
              'movies', 'episode_length', 'genre', \
              'year', 'douban_rating', 'bangumi_tv_rating', \
              'douban_link', 'bangumi_tv_link', 'description', \
              'season', 'release_date', 'broadcast_day', \
              'status', 'start_date', 'end_date', 'times_watched', \
              'story', 'illustration', 'music', 'passion', \
              'dmhy_search_terms', 'dmhy_tags', 'delayed_weeks')
  
  id = Int()
  rankings = JSONString(season=String())

  def resolve_id(parent, info):
    return parent.id

  def resolve_rankings(parent, info):
    rankings_objs = SeasonRanking.objects.filter(
      anime_id = parent.id,
      season = parent.season
    ).order_by('date')
    res_dict = {parent.season: {}}
    for r_obj in rankings_objs:
      res_dict[parent.season][r_obj.date.strftime('%Y-%m-%d')] = r_obj.ranking
    return json.dumps(res_dict, ensure_ascii=False)

class DoubanInfoNode(ObjectType):
  name_zh = String()
  name_jp = String()
  douban_rating = Float()
  year = String()
  tv_episodes = Int()
  episode_length = Int()
  description = String()
  html = String()

class ScrapeResultNode(ObjectType):
  name_zh = String()
  name_jp = String()
  cover_url = String()
  tv_episodes = Int()
  episode_length = Int()
  douban_rating = Float()
  bangumi_tv_rating = Float()
  genre = String()
  year = String()
  douban_link = String()
  bangumi_tv_link = String()
  description = String()
  season = String()
  release_date = String()
  broadcast_day = String()

class SearchResultNode(ObjectType):
  name = String()
  type = String()
  url = String()

class DownloadLinkResult(ObjectType):
  name = String()
  page_url = String()
  magnet_url = String()

class SearchDownloadLinkResultNode(ObjectType):
  res_list = List(DownloadLinkResult)
  msg = String()

class Query(ObjectType):
  get_animes = List(AnimeNode)
  search_bangumi_tv = List(SearchResultNode, search_term=String())
  search_douban = List(SearchResultNode, search_term=String())
  get_anime_info = Field(ScrapeResultNode, bangumi_tv_url=String(), douban_url=String())
  get_download_link = Field(SearchDownloadLinkResultNode, id=Int())

  def resolve_get_animes(self, info, **kwargs):
    return Anime.objects.all().order_by('-end_date')

  def resolve_search_bangumi_tv(self, info, search_term):
    return [SearchResultNode(**search_res) for search_res in bangumi_tv_search(search_term)]

  def resolve_search_douban(self, info, search_term):
    return [SearchResultNode(**search_res) for search_res in douban_search(search_term)]

  def resolve_get_anime_info(self, info, bangumi_tv_url, douban_url):
    scrape_res = get_anime_info(bangumi_tv_url, douban_url)
    return ScrapeResultNode(**scrape_res)

  def resolve_get_download_link(self, info, id):
    return SearchDownloadLinkResultNode(**dmhy_search_download_links(id))