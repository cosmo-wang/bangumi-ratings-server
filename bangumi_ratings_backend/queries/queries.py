import graphene
from graphene_django import DjangoObjectType
from bangumi_ratings_backend.models import Anime, SeasonAnime, SeasonRanking, Quote
import datetime
import urllib3
import re
import json

class AnimeNode(DjangoObjectType):
  class Meta:
    model = Anime
    fields = ('name_zh', 'name_jp', 'tv_episodes', \
              'movies', 'episode_length', 'status', 'genre', \
              'year', 'douban_rating', 'douban_link', 'description', 'start_date', \
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

class DoubanInfoNode(graphene.ObjectType):
  name_zh = graphene.String()
  name_jp = graphene.String()
  douban_rating = graphene.Float()
  year = graphene.String()
  tv_episodes = graphene.Int()
  episode_length = graphene.Int()
  description = graphene.String()
  html = graphene.String()

class Query(graphene.ObjectType):
  get_animes = graphene.List(AnimeNode)
  get_season_schedules = graphene.List(AnimeScheduleNode)
  get_douban_info = graphene.Field(DoubanInfoNode, douban_link=graphene.String())

  def resolve_get_animes(self, info, **kwargs):
    return Anime.objects.all().order_by('-end_date')

  def resolve_get_season_schedules(self, info):
    return SeasonAnime.objects.all().order_by('release_date')

  def resolve_get_douban_info(self, info, douban_link):
    http_pool = urllib3.PoolManager()
    html_source = http_pool.request('GET', douban_link).data.decode('utf-8').replace('\n', '')

    # get names and year
    search_res = re.search('<h1>(.)*</h1>', html_source)
    name_year_matched = html_source[search_res.start():search_res.end()]
    year = re.sub(r'<h1>.*<span class="year">\(|\)</span>.*</h1>', '', name_year_matched)
    names = re.sub(r'<h1>.*<span property="v:itemreviewed">|</span> .*<span class="year">\(.*\)</span>.*</h1>', '', name_year_matched).split(' ')
    if len(names) == 2:
      name_zh = names[0]
      name_jp = names[1]
    else:
      name_zh = names[0]
      name_jp = ''
    # get douban rating
    search_res = re.search('>\d.\d</strong>', html_source)
    douban_rating = search_res.group().replace('</strong>', '').replace('>', '').replace(' ', '') if search_res else 0.0
    # get episodes
    search_res = re.search('集数:.*([0-9]+)<br', html_source)
    if search_res:
      tv_episodes = search_res.group().replace('集数:</span>', '').replace(' ', '')
      tv_episodes = re.sub('<br.*', '', tv_episodes)
    else:
      tv_episodes = 0
    # get episode length
    search_res = re.search('单集片长:</span>.*\d分钟', html_source)
    if search_res:
      episode_length = search_res.group().replace('单集片长:</span>', '').replace(' ', '')
      episode_length = re.sub('分钟(<br.*)?', '', episode_length)
    else:
      episode_length = 0
    # get description
    search_res = re.search(r'<span class=\"all hidden\">.*id=\"dale_movie_subject_banner_after_intro', html_source)
    if not search_res:
      search_res = re.search(r'property=\"v:summary\".*id=\"dale_movie_subject_banner_after_intro', html_source)
    if search_res:
      description = re.sub('</span>.*', '', search_res.group())
      description = re.sub('.*class="">', '', description).strip().replace('<br />', '\n')
    else:
      description = ''

    return DoubanInfoNode(
      name_zh=name_zh,
      name_jp=name_jp,
      year=year,
      douban_rating=douban_rating,
      tv_episodes=tv_episodes,
      episode_length=episode_length,
      description=description,
      html=html_source
    )