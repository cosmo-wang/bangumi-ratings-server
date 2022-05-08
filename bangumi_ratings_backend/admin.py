from django.contrib import admin
from bangumi_ratings_backend.models import Anime, SeasonAnime, SeasonRanking

IGNORED_FIELDS = ['anime_id']

def get_options_name(model):
  return [field.name for field in model._meta.get_fields() if field.name not in IGNORED_FIELDS]

class BangumiRatingsServerAdminSite(admin.AdminSite):
  site_header = "Bangumi Ratings Server Admin"
  site_title = "Bangumi Ratings Server"
  index_title = "Bangumi Ratings Server"
  site_url = "/bangumi_ratings_server/"

class AnimeAdmin(admin.ModelAdmin):
  list_filter = ['status', 'genre', 'year', 'times_watched', 'season']
  list_display = search_fields = ['id', 'name_zh'] + list_filter

class SeasonAnimeAdmin(admin.ModelAdmin):
  list_display = list_filter = get_options_name(SeasonAnime)
  search_fields = ['name_zh']

class SeasonRankingAdmin(admin.ModelAdmin):
  list_display = search_fields = get_options_name(SeasonRanking)
  search_fields = ['anime_id']
  list_filter = ['season', 'date']


admin_site = BangumiRatingsServerAdminSite(name="bangumi-ratings-server-admin")
admin_site.register(Anime, AnimeAdmin)
admin_site.register(SeasonAnime, SeasonAnimeAdmin)
admin_site.register(SeasonRanking, SeasonRankingAdmin)
