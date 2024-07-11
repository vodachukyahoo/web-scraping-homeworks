import requests
from bs4 import BeautifulSoup
from pprint import pprint
import urllib.parse
import json


def get_content(url):
    response = requests.get(
        url=url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
    )
    return response.text


def write_json(data):
    filename = 'bbc_news_with_topics.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_news_with_topics(url):
    response = get_content(url)
    soup = BeautifulSoup(response, 'html.parser')

    articles = soup.find_all('div',
                             class_='ssrcss-1va2pun-UncontainedPromoWrapper eqfxz1e5')
    news_list = []
    topics = []
    not_live_news_list = []

    # Add this check to not get LIVE news, because there aren't 'Related Topics'
    for article in articles:
        if article.contents[0].attrs['type'] == 'article':
            not_live_news_list.append(article)
        # Get only first 5 Articles for result list
        if len(not_live_news_list) == 5:
            break

    for news in not_live_news_list:
        link = news.find('a')['href']
        if 'http' not in link:
            parsed_url = urllib.parse.urlparse(url)
            site_link = parsed_url.scheme + '://' + parsed_url.netloc
            link = site_link + link
        article_response = get_content(link)
        article_soup = BeautifulSoup(article_response, 'html.parser')

        topics_soup = article_soup.find_all('div',
                                            class_='ssrcss-smoc0a-StyledTagContainer ed0g1kj1')
        for topic in topics_soup:
            topics = [i.text for i in topic.find_all('li')]
        news_list.append({
            'Link': link,
            'Topics': topics
        })

    return news_list


if __name__ == '__main__':
    url = 'https://www.bbc.com/sport'
    news = get_news_with_topics(url=url)
    pprint(news)
    write_json(news)
