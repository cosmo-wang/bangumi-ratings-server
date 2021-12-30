from django.db import models

class Anime(models.Model):
  name_zh = models.CharField(unique=True, max_length=255)
  name_jp = models.CharField(max_length=255, blank=True)
  tv_episodes = models.IntegerField(default=12)
  movies = models.IntegerField(default=0)
  episode_length = models.IntegerField(default=24)
  status = models.CharField(max_length=10)
  genre = models.CharField(max_length=255)
  year = models.CharField(max_length=10, blank=True)
  douban_rating = models.FloatField(default=0, blank=True)
  description = models.TextField(default='', blank=True)
  start_date = models.DateField(blank=True, null=True)
  end_date = models.DateField(blank=True, null=True)
  times_watched = models.IntegerField(default=0)

  def __str__(self):
    return f'{self.name_zh}, {self.start_date}, {self.end_date}, {self.douban_rating}'

class AnimeRating(models.Model):
  anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
  story = models.FloatField(default=0)
  illustration = models.FloatField(default=0)
  music = models.FloatField(default=0)
  passion = models.FloatField(default=0)

  def __str__(self):
    anime_name = Anime.objects.get(id = self.anime_id).name_zh
    return f'{anime_name}, {self.story}, {self.illustration}, {self.music}, {self.passion}'

class SeasonAnimes(models.Model):
  anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
  season = models.CharField(max_length=255)
  release_date = models.DateField(blank=True, null=True)
  broadcast_day = models.CharField(max_length=255, blank=True, null=True)

class SeasonRanking(models.Model):
  anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
  season = models.CharField(max_length=255)
  date = models.DateField()
  ranking = models.IntegerField(default=0)

  def __str__(self):
    anime_name = Anime.objects.get(id = self.anime_id).name_zh
    return f'{anime_name}, {self.season}, {self.date}, {self.ranking}'

class Quote(models.Model):
  anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
  content = models.TextField()
  content_zh = models.TextField()
  month = models.CharField(max_length=255)
  person = models.CharField(max_length=255)
  
