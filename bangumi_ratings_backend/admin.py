from django.contrib import admin
from bangumi_ratings_backend.models import Anime, AnimeRating, SeasonAnimes, SeasonRanking, Quote

IGNORED_FIELDS = ['anime_id']

def get_options_name(model):
  return [field.name for field in model._meta.get_fields() if field.name not in IGNORED_FIELDS]

class BangumiRatingsServerAdminSite(admin.AdminSite):
  site_header = "Bangumi Ratings Server Admin"
  site_title = "Bangumi Ratings Server"
  index_title = "Bangumi Ratings Server"
  site_url = "/bangumi_ratings_server/"

class AnimeAdmin(admin.ModelAdmin):
  list_filter = ['status', 'genre', 'year', 'times_watched']
  list_display = search_fields = ['id', 'name_zh'] + list_filter

class AnimeRatingAdmin(admin.ModelAdmin):
  list_display = search_fields = get_options_name(AnimeRating)
  list_filter = ['anime_id']

class SeasonAnimesAdmin(admin.ModelAdmin):
  list_display = list_filter = search_fields = get_options_name(SeasonAnimes)

class SeasonRankingAdmin(admin.ModelAdmin):
  list_display = search_fields = get_options_name(SeasonRanking)
  list_filter = ['season', 'date']

class QuoteAdmin(admin.ModelAdmin):
  list_display = list_filter = search_fields = get_options_name(Quote)

admin_site = BangumiRatingsServerAdminSite(name="bangumi-ratings-server-admin")
admin_site.register(Anime, AnimeAdmin)
admin_site.register(AnimeRating, AnimeRatingAdmin)
admin_site.register(SeasonAnimes, SeasonAnimesAdmin)
admin_site.register(SeasonRanking, SeasonRankingAdmin)
admin_site.register(Quote, QuoteAdmin)
