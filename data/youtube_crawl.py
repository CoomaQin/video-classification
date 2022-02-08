from bs4 import BeautifulSoup  # for scraping
import requests  # required for reading the file
import json
import os
import gdata.youtube
import gdata.youtube.service


def scrape_video(url, yt_service):
    Vid = {}
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
    title = soup.findAll('meta')[2].get("content")
    div_s = soup.findAll('link')
    print(div_s)
    Vid['Title'] = title
    Vid['Link'] = url
    related_feed = yt_service.GetYouTubeRelatedVideoFeed(video_id='abc123')
    Vid['Related'] = related_feed


    # Title_Related = []
    # Link_Related = []
    # for i in range(len(Related_videos)):
    #     Title_Related.append(Related_videos[i].get('title'))
    #     Link_Related.append(Related_videos[i].get('href'))
    # Related_dictionary = dict(zip(Title_Related, Link_Related))
    # Vid['Related_vids'] = Related_dictionary


def save(Vid, name="vfile.json"):
    with open(name, 'w', encoding='utf8') as ou:
        json.dump(Vid, ou, ensure_ascii=False)


if __name__ == "__main__":
    yt_service = gdata.youtube.service.YouTubeService()
    scrape_video("https://www.youtube.com/watch?v=sxlYzjBYSjQ", yt_service)