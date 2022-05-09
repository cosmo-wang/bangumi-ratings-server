from django.db import models

class Anime(models.Model):
  # basic info
  name_zh = models.CharField(unique=True, max_length=255)
  name_jp = models.CharField(max_length=255, blank=True)
  cover_url = models.URLField(max_length=255, blank=True)
  tv_episodes = models.IntegerField(default=12)
  episode_length = models.IntegerField(default=24)
  genre = models.CharField(max_length=255)  # seperated by /
  year = models.CharField(max_length=10, blank=True)
  bangumi_tv_rating = models.FloatField(default=0, blank=True)
  bangumi_tv_link = models.URLField(max_length=255, blank=True)
  description = models.TextField(default='', blank=True)
  season = models.CharField(max_length=255, default='')
  release_date = models.DateField(blank=True, null=True)
  broadcast_day = models.CharField(max_length=255, blank=True, null=True)
  # personal info
  status = models.CharField(max_length=10)
  start_date = models.DateField(blank=True, null=True)
  end_date = models.DateField(blank=True, null=True)
  times_watched = models.IntegerField(default=0)
  story = models.FloatField(default=0)
  illustration = models.FloatField(default=0)
  music = models.FloatField(default=0)
  passion = models.FloatField(default=0)
  # download info
  dmhy_search_terms = models.TextField(default='', blank=True)  # seperated by ,
  dmhy_tags = models.TextField(default='Lilith-Raws,NC-Raws,ANi', blank=True)  # seperated by ,
  delayed_weeks = models.IntegerField(default=0)

  def save(self, *args, **kwargs):
    if not self.dmhy_search_terms:
      self.dmhy_search_terms = self.name_zh
    super(Anime, self).save(*args, **kwargs)

  def __str__(self):
    return f'{self.name_zh}, {self.start_date}, {self.end_date}'

class SeasonRanking(models.Model):
  anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
  season = models.CharField(max_length=255)
  date = models.DateField()
  ranking = models.IntegerField(default=0)

  def __str__(self):
    anime_name = Anime.objects.get(id = self.anime_id).name_zh
    return f'{anime_name}, {self.season}, {self.date}, {self.ranking}'
