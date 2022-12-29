from datetime import datetime
import urllib3
import re
from bangumi_ratings_backend.models import Anime
from bs4 import BeautifulSoup

search_res_max = 10

bangumi_tv_search_url = 'http://bangumi.tv/subject_search/{}?cat=all'
bangumi_tv_base_url = 'http://bangumi.tv'
bangumi_tv_type_map = {
  'subject_type_1': '[书籍]',
  'subject_type_2': '[动漫]',
  'subject_type_3': '[音乐]',
  'subject_type_4': '[游戏]',
  'subject_type_6': '[三次元]'
}

dmhy_search_url = 'http://www.dmhy.org/topics/list/page/{}?keyword={}'
dmhy_base_url = 'http://www.dmhy.org'
dmhy_page_size = 80

zh_date_pattern = '(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日'

weekday_map = {
  1: '星期一',
  2: '星期二',
  3: '星期三',
  4: '星期四',
  5: '星期五',
  6: '星期六',
  7: '星期日'
}

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

def get_anime_info(bangumi_tv_url):
  def get_text_by_css_or_default(soup, selector, default):
    elements = soup.select(selector)
    if elements:
      extracted_text = elements[0].find(text=True, recursive=False)
      if isinstance(default, int) and (not extracted_text.isnumeric()):
        return default
      else:
        return extracted_text
    return default

  http_pool = urllib3.PoolManager()
  # get info from bangumi TV
  bangumi_tv_source = http_pool.request('GET', bangumi_tv_url).data.decode('utf-8')
  soup = BeautifulSoup(bangumi_tv_source, 'html.parser')
  name_jp_elements = soup.select("h1.nameSingle a")
  name_jp = name_jp_elements[0].text if name_jp_elements else ''
  name_zh = get_text_by_css_or_default(soup, "#infobox li:contains(中文名)", name_jp)
  cover_url = 'https:' + soup.select("a.cover")[0]['href']
  tv_episodes = get_text_by_css_or_default(soup, "#infobox li:contains(话数)", 12)
  bangumi_tv_rating = get_text_by_css_or_default(soup, ".global_score .number", 0.0)
  genre_elements = soup.select(".subject_tag_section .inner span")
  genre = ','.join([genre_element.text for genre_element in genre_elements])
  release_date = get_text_by_css_or_default(soup, "#infobox li:contains(放送开始)", '')
  if not release_date:
    release_date = get_text_by_css_or_default(soup, "#infobox li:contains(上映年度)", '')
  episode_length = re.sub('[^0-9]','', get_text_by_css_or_default(soup, "#infobox li:contains(片长)", '24'))
  date_match = re.match(zh_date_pattern, release_date)
  release_date = datetime(int(date_match.group('year')), int(date_match.group('month')), int(date_match.group('day')))
  broadcast_day = get_text_by_css_or_default(soup, "#infobox li:contains(放送星期)", weekday_map[release_date.isoweekday()])
  release_date = release_date.strftime('%Y-%m-%d')
  year = date_match.group('year')
  season = date_match.group('year') + "年" + date_match.group('month') + "月"
  description_elements = soup.select('#subject_summary')
  description = description_elements[0].text if description_elements else ''

  return {
    'name_zh': name_zh,
    'name_jp': name_jp,
    'cover_url': cover_url,
    'tv_episodes': tv_episodes,
    'episode_length': episode_length,
    'bangumi_tv_rating': bangumi_tv_rating,
    'genre': genre,
    'year': year,
    'bangumi_tv_link': bangumi_tv_url,
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
  res_list = []
  found_names = set()
  search_term_not_found = True
  tag_not_found = True
  episode_not_found = True
  for search_term in search_terms:
    entries = search_on_dmhy(search_term, 20)
    for entry in entries:
      a_tags = entry.find('td', {'class': 'title'}).find_all('a')
      if len(a_tags) > 1:
        title_element = entry.find('td', {'class': 'title'}).find_all('a')[1]
      else:
        title_element = entry.find('td', {'class': 'title'}).find_all('a')[0]
      entry_name = title_element.text.strip()
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
                res['time'] = entry.find_all('td')[0].find(text=True).strip()
                res['type'] = entry.find_all('td')[1].text.strip()
                res['name'] = entry_name
                res['page_url'] = dmhy_base_url + title_element['href']
                res['magnet_url'] = entry.find('a', {'title': '磁力下載'})['href']
                res['size'] = entry.find_all('td')[4].text.strip()
                res_list.append(res)
    msg = ''
    if search_term_not_found:
      msg += f'未找到关键字：{search_terms}相关条目。'
    elif tag_not_found:
      msg += f'未找到标签：{tags}相关条目。'
    elif episode_not_found:
      msg += f'未找到第{latest_episode}集相关条目。'
  return {'title': f'第{latest_episode}集搜索结果','res_list': res_list, 'msg': msg}

def dmhy_search(search_term, max_search_results):
  entries = search_on_dmhy(search_term, max_search_results)
  res_list = []
  found_names = set()
  msg = ''
  for entry in entries:
    a_tags = entry.find('td', {'class': 'title'}).find_all('a')
    if len(a_tags) > 1:
      title_element = entry.find('td', {'class': 'title'}).find_all('a')[1]
    else:
      title_element = entry.find('td', {'class': 'title'}).find_all('a')[0]
    entry_name = title_element.text
    if entry_name not in found_names:
      found_names.add(entry_name)
      res = {}
      res['time'] = entry.find_all('td')[0].find(text=True).strip() + ' GMT+8'
      res['type'] = entry.find_all('td')[1].text.strip()
      res['name'] = entry_name
      res['page_url'] = dmhy_base_url + title_element['href']
      res['magnet_url'] = entry.find('a', {'title': '磁力下載'})['href']
      res['size'] = entry.find_all('td')[4].text
      res_list.append(res)
  print(len(res_list))
  if not res_list:
    msg = '无结果'
  return {'title': f'{search_term}搜索结果','res_list': res_list, 'msg': msg}


def search_on_dmhy(search_term, max_search_results):
  http_pool = urllib3.PoolManager()
  res = []
  page = 1
  remaing_to_get = max_search_results
  while (len(res) < max_search_results):
    search_result_page = http_pool.request('GET', dmhy_search_url.format(page, search_term.replace(' ', '+'))).data.decode('utf-8')
    soup = BeautifulSoup(search_result_page, 'html.parser')
    cur_page_res = soup.select('table.tablesorter tbody tr')
    cur_page_count = len(cur_page_res)
    if (cur_page_count > remaing_to_get):
      res += cur_page_res[:remaing_to_get]
      break
    else:
      res += cur_page_res
    remaing_to_get -= cur_page_count
    if cur_page_count < dmhy_page_size: break
    page += 1
  return res