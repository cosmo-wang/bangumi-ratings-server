from django.contrib import admin
from bangumi_ratings_backend.models import TestModel

class BangumiRatingsServerAdminSite(admin.AdminSite):
  site_header = "Bangumi Ratings Server Admin"
  site_title = "Bangumi Ratings Server"
  index_title = "Bangumi Ratings Server"
  site_url = "/bangumi_ratings_server/"

class TestModelAdmin(admin.ModelAdmin):
  list_display = list_filter = search_fields = ["name"]

admin_site = BangumiRatingsServerAdminSite(name="bangumi-ratings-server-admin")
admin_site.register(TestModel, TestModelAdmin)
