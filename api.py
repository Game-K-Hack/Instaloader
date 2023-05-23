import os
from fake_useragent import UserAgent
from utils import download as dld

import cfscrape
import cloudscraper

import requests


CFSCRAPE = cfscrape.create_scraper()
CLOUDSCRAPER = cloudscraper.create_scraper()


class InstaStories:

    def __init__(self, username) -> None:
        self.username = username
        self.dirpath = "./download"
        self.dirpath = f"{self.dirpath}/{self.username}"
        if not os.path.exists(self.dirpath):
            os.makedirs(self.dirpath)
        self.stories = {}
        self.scraper = None

    def set_scraper(self, scraper:object) -> None:
        self.scraper = scraper

    def download(self):
        self.check_file()
        for key in self.stories.keys():
            filename = f"{self.dirpath}/{key}.{'mp4' if '.mp4?' in self.stories[key] else 'jpg'}"
            dld(self.stories[key], filename)
            print(f"[+] Story downloaded (id:{key})")

    def check_file(self):
        dirlist = [i.split(".")[0] for i in os.listdir(self.dirpath)]
        rmkey = [key for key in self.stories.keys() if key in dirlist]
        for key in rmkey:
            self.stories.pop(key)

    def save_insta_com(self):
        ua = UserAgent()
        res = self.scraper.post(
            url="https://www.save-insta.com/process",
            headers={
                "User-Agent": ua.firefox,
                "Referer": "https://www.save-insta.com/fr/story-downloader/",
                "X-Valy-Cache": "accpted",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.save-insta.com"
            },
            data={
                "instagram_url": self.username,
                "type": "story",
                "resource": "save"
            }).content.decode("utf8")
        res = eval(
            res.replace("null", "''").replace("false",
                                              "False").replace("true", "True"))
        self.stories = {i["id"]: i["src"] for i in res["result"]["playlist"]}
        return len(self.stories)
    
class response:
    def __init__(self, username) -> None:
        self.username = username
        self.story = list()
        self.path = f"./download/{username}/"
        try: os.makedirs(self.path)
        except: pass

    def setStory(self, urls:list) -> None:
        self.story = urls

    def addStory(self, name:str, url:str) -> None:
        self.story.append({
            "name":name, 
            "url":url
        })
    
    def download(self) -> None:
        for i, url in enumerate(self.story):
            print(f"[*] Download... {(100*i) // len(self.story)} %", end="\r")
            with requests.get(url["url"], stream=True) as res:
                res.raise_for_status()
                with open(self.path + url["name"], "wb") as file:
                    for chunk in res.iter_content(chunk_size=8192): 
                        file.write(chunk)
        print(f"[+] Downloaded 100 %")
    
class instasupersave:
    def __init__(self, username, id, scraper) -> None:
        self.username = username
        self.id = str(id)
        self.resObject = response(username)
        self.scraper = scraper

    def getStory(self) -> response:
        # 
        res = self.scraper.get(f"https://instasupersave.com/api/ig/stories/{self.id}")
        # Decode response of the request
        res = res.content.decode("utf8")
        # Convert str to dict (json)
        res = eval(res.replace("true", "True").replace("false", "False"))
        # Add in response object
        for story in res["result"]:
            # 
            if "video_versions" in story.keys():
                k, ext = "video_versions", ".mp4"
            elif "image_versions2" in story.keys():
                k, ext = "image_versions2", ".png"
            else:
                raise "Key not found"
            # 
            if type(story[k]) != list and "candidates" in story[k].keys():
                story[k] = story[k]["candidates"]
            # Search the high quality of video or photo
            index, h = 0, 0
            for i, elm in enumerate(story[k]):
                if elm["height"] > h:
                    h = elm["height"]
                    index = i
            # The index the place of the high quality in list
            self.resObject.addStory(
                name = story["pk"] + ext, 
                url = story[k][index]["url"])
        # 
        return self.resObject
