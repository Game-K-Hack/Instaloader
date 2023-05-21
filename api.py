import os
import requests
from fake_useragent import UserAgent
from utils import download as dld

import cfscrape
import cloudscraper


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
