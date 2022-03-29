from bs4 import BeautifulSoup  # for scraping
import requests  # required for reading the file
import json
import os
import re
import requests


def get_video_info(vid):
    vinfo = {}
    related_video = set()
    header = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    url = f"https://www.youtube.com/watch?v={vid}"
    source = requests.get(url, headers=header).text
    soup = BeautifulSoup(source, "html5lib")
    scripts = soup.findAll('script')
    related_video_script = str(scripts[38])
    indices_object = re.finditer(pattern='"videoId"', string=related_video_script)
    indices = [index.start() for index in indices_object]
    for idx in indices:
        related_video.add(related_video_script[idx + 11: idx + 22])

    title = soup.findAll('meta')[2].get("content")
    vinfo['title'] = title
    vinfo['id'] = vid
    vinfo['related_video'] = related_video
    return vinfo


def scrape_related_video(start, token):
    stack = [start]
    visited = set()
    videos = []
    while stack:
        curr_id = stack.pop()
        get_related_video_url = f"https://www.googleapis.com/youtube/v3/search"
        get_related_video_params = {
            'part': 'snippet', 'relatedToVideoId': curr_id, 'type': 'video', 'key': token}
        res = requests.get(url=get_related_video_url,
                           params=get_related_video_params).json()
        print(res)
        if "item" in res:
            raw_related_video = res['items']
            for vitem in raw_related_video:
                next_id = vitem["id"]["videoId"]
                if "snippet" in vitem and next_id not in visited:
                    videos.append(vitem)
                    stack.append(next_id)
        visited.add(curr_id)
    return videos


def save(Vid, name="vfile.json"):
    with open(name, 'w', encoding='utf8') as ou:
        json.dump(Vid, ou, ensure_ascii=False)


if __name__ == "__main__":
    # scrape_related_video(
    #     "sxlYzjBYSjQ", "AIzaSyAeZWa8IBwhcLtmflBaeNDX3eIMrJnid_4")
    get_video_info("eVTXPUF4Oz4")
