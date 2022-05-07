from datetime import datetime
import urllib3
import re
from bangumi_ratings_backend.models import Anime
from bs4 import BeautifulSoup

search_res_max = 10

bangumi_tv_search_url = 'http://bangumi.tv/subject_search/{}?cat=2'
bangumi_tv_base_url = 'http://bangumi.tv'
bangumi_tv_type_map = {
  'subject_type_1': '[书籍]',
  'subject_type_2': '[动漫]',
  'subject_type_3': '[音乐]',
  'subject_type_4': '[游戏]',
  'subject_type_6': '[三次元]'
}

douban_search_url = 'https://www.douban.com/search?q={}'
douban_url_pattern = '.*url=(?P<url>[^&]+)&.*'

dmhy_search_url = 'http://www.dmhy.org/topics/list?keyword={}'
dmhy_base_url = 'http://www.dmhy.org'

zh_date_pattern = '(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日'

def bangumi_tv_search(search_term):
  http_pool = urllib3.PoolManager()
  html_source = http_pool.request('GET', bangumi_tv_search_url.format(search_term)).data.decode('utf-8')
  soup = BeautifulSoup(html_source, 'html.parser')
  res_elements = soup.select('#browserItemList li .inner')
  
  def get_type(res_element):
    type_icon = res_element.find('span', {'class': 'ico_subject_type'})
    type_class = type_icon['class'][1]
    if type_class in bangumi_tv_type_map:
      return bangumi_tv_type_map[type_class]
    else:
      return '未知类型'

  if res_elements:
    res_elements = res_elements[:min(len(res_elements), search_res_max)]
    res_list = []
    for res_element in res_elements:
      res_list.append({
        'name': res_element.h3.a.text,
        'type': get_type(res_element),
        'url': bangumi_tv_base_url + res_element.h3.a['href']
      })
    return res_list
  else:
    return []
  
def douban_search(search_term):
  http_pool = urllib3.PoolManager()
  html_source = http_pool.request('GET', douban_search_url.format(search_term)).data.decode('utf-8')
  soup = BeautifulSoup(html_source, 'html.parser')
  all_res_list = soup.select('.result-list .result h3')
  if all_res_list:
    all_res_list = all_res_list[:min(len(all_res_list), search_res_max)]
    res_list = []
    for res_element in all_res_list:
      name = res_element.a.text
      type_element = res_element.span
      type = type_element.text if type_element else ""
      url_match = re.match(douban_url_pattern, res_element.a['href'])
      url = url_match.group('url').replace('%3A', ':').replace('%2F', '/')
      res_list.append({'name': name, 'type': type, 'url': url})
    return res_list
  else:
    return []

def get_anime_info(bangumi_tv_url, douban_url):
  def get_text_by_css_or_default(soup, selector, default):
    elements = soup.select(selector)
    return elements[0].find(text=True, recursive=False) if elements else default

  http_pool = urllib3.PoolManager()
  # get info from bangumi TV
  bangumi_tv_source = http_pool.request('GET', bangumi_tv_url).data.decode('utf-8')
  soup = BeautifulSoup(bangumi_tv_source, 'html.parser')
  name_jp = soup.select("h1.nameSingle a")[0].text
  name_zh = get_text_by_css_or_default(soup, "#infobox li:contains(中文名)", name_jp)
  cover_url = 'https:' + soup.select("a.cover")[0]['href']
  tv_episodes = get_text_by_css_or_default(soup, "#infobox li:contains(话数)", 12)
  bangumi_tv_rating = soup.select(".global_score .number")[0].find(text=True, recursive=False)
  genre_elements = soup.select(".subject_tag_section .inner span")
  genre = ','.join([genre_element.text for genre_element in genre_elements])
  release_date = soup.select("#infobox li:contains(放送开始)")[0].find(text=True, recursive=False)
  date_match = re.match(zh_date_pattern, release_date)
  release_date = datetime(int(date_match.group('year')), int(date_match.group('month')), int(date_match.group('day')))
  release_date = release_date.strftime('%Y-%m-%d')
  year = date_match.group('year')
  season = date_match.group('year') + "年" + date_match.group('month') + "月"
  broadcast_day = soup.select("#infobox li:contains(放送星期)")[0].find(text=True, recursive=False)
  description = soup.select('#subject_summary')[0].text

  # get info from douban
  douban_source = http_pool.request('GET', douban_url).data.decode('utf-8')
  soup = BeautifulSoup(douban_source, 'html.parser')
  episode_length_search_res = re.search('单集片长:</span>.*\d分钟', douban_source)
  if episode_length_search_res:
    episode_length = episode_length_search_res.group().replace('单集片长:</span>', '').replace(' ', '')
    episode_length = re.sub('分钟(<br.*)?', '', episode_length)
  else:
    episode_length = 24
  douban_rating = soup.select('strong.rating_num')[0].text
  if not douban_rating:
    douban_rating = 0

  return {
    'name_zh': name_zh,
    'name_jp': name_jp,
    'cover_url': cover_url,
    'tv_episodes': tv_episodes,
    'episode_length': episode_length,
    'bangumi_tv_rating': bangumi_tv_rating,
    'douban_rating': douban_rating,
    'genre': genre,
    'year': year,
    'bangumi_tv_link': bangumi_tv_url,
    'douban_link': douban_url,
    'season': season,
    'release_date': release_date,
    'broadcast_day': broadcast_day,
    'description': description,
  }

def dmhy_search_download_links(id):
  def search_term_match(search_term, entry_name):
    if ' ' in search_term:
      for splitted in search_term.split(' '):
        if splitted in entry_name:
          return True
      return False
    else:
      return search_term in entry_name

  # get anime info
  anime_obj = Anime.objects.get(id=id)
  search_terms = anime_obj.dmhy_search_terms.split(',')
  tags = anime_obj.dmhy_tags.split(',')
  # get latest episode
  delayed_weeks = anime_obj.delayed_weeks
  delta = datetime.now().date() - anime_obj.release_date
  latest_episode = delta.days // 7 + 1 - delayed_weeks
  if (anime_obj.tv_episodes != 0 and latest_episode > anime_obj.tv_episodes):
    return {'res_list': [], 'msg': f'{anime_obj.name_zh}已更新完毕，请前往动漫花园下载季度全集。'}
  latest_episode = '0' + str(latest_episode) if latest_episode < 10 else str(latest_episode)
  
  # start searching
  http_pool = urllib3.PoolManager()
  res_list = []
  found_names = set()
  search_term_not_found = True
  tag_not_found = True
  episode_not_found = True
  for search_term in search_terms:
    search_result_page = http_pool.request('GET', dmhy_search_url.format(search_term.replace(' ', '+'))).data.decode('utf-8')
    soup = BeautifulSoup(search_result_page, 'html.parser')
    entries = soup.select('table.tablesorter tbody tr')
    for entry in entries:
      a_tags = entry.find('td', {'class': 'title'}).find_all('a')
      if len(a_tags) > 1:
        title_element = entry.find('td', {'class': 'title'}).find_all('a')[1]
      else:
        title_element = entry.find('td', {'class': 'title'}).find_all('a')[0]
      entry_name = title_element.text
      if entry_name not in found_names:
        for tag in tags:
          if search_term_match(search_term, entry_name):
            search_term_not_found = False
            if tag in entry_name:
              tag_not_found = False
              if latest_episode in entry_name:
                found_names.add(entry_name)
                episode_not_found = False
                res = {}
                res['name'] = entry_name
                res['page_url'] = dmhy_base_url + title_element['href']
                res['magnet_url'] = entry.find('a', {'title': '磁力下載'})['href']
                res_list.append(res)
    msg = ''
    if search_term_not_found:
      msg += f'未找到关键字：{search_terms}相关条目。'
    elif tag_not_found:
      msg += f'未找到标签：{tags}相关条目。'
    elif episode_not_found:
      msg += f'未找到第{latest_episode}集相关条目。'
  return {'res_list': res_list, 'msg': msg}
  