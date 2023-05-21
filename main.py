import os
import api
import utils
from mega import Mega
import datetime
import instaloader
from fake_useragent import UserAgent
# define class
# class Core:
#     login = "Votre utilisateur"
#     paswd = "Votre mot de passe"
#     user_list = ["user1", "user2", ...]
# or import lib
from core import Core

# Define Mega
mega = Mega()
# Connect to Mega
m = mega.login(Core.login, Core.paswd)

L = instaloader.Instaloader(user_agent=UserAgent().firefox)

space = m.get_storage_space(kilo=True)
if space["used"] > space["total"]-10000:
    print("[!] Storage soon full")

current_time = str(datetime.datetime.now()).split(" ")[0]

for username in Core.user_list:

    print(f"[*] Scan {username} profile...")

    folder = m.find(username, exclude_deleted=True)
    if folder is None:
        m.create_folder(username)

    profile = instaloader.Profile.from_username(L.context, username)

    print("[*] Get post...")
    posts_dict = {}
    for post in profile.get_posts():
        # post.caption
        date = str(post.date).split(' ')[0].replace("/", "-")
        if current_time != date:
            if posts_dict == {}:
                print("[i] No post today")
            break
        if date not in posts_dict.keys():
            posts_dict[date] = []
        for i, p in enumerate(post.get_sidecar_nodes()):
            posts_dict[date].append({
                "name": f"{post.mediaid}-{i}", 
                "url": p.video_url if p.is_video else p.display_url, 
                "is_video": p.is_video
            })
        post_url = post.url if post.video_url is None else post.video_url
        if len(posts_dict[date]) == 0 or post_url not in [i["url"] for i in posts_dict[date]]:
            posts_dict[date].append({
                "name": f"{post.mediaid}", 
                "url": post_url, 
                "is_video": False if post.video_url is None else True
            })
    print("[+] Post scanned")

    for key in posts_dict.keys():
        pbar = utils.progress_bar(len(posts_dict[key].keys())+1)
        for post in posts_dict[key]:
            utils.download(post["url"], f"./download/{username}/{post['name']}.{'mp4' if post['is_video'] else 'jpg'}")
            print(f"[*] ({key}) Download {pbar.update()}", end='\r')
        print(f"\r[+] ({key}) Downloaded {pbar.update()}")

    print("[*] Get stories...")
    # Set profile
    insta = api.InstaStories(username)
    insta.set_scraper(api.CFSCRAPE)
    # Scan storie on save-insta-com website
    insta.save_insta_com()
    # Download storie
    insta.download()
    print("[+] Stories scanned")

    if len(os.listdir(f"./download/{username}")) != 0:
        print("[*] Upload on Mega...")
        dirname = username + "/" + str(datetime.datetime.now()).split(" ")[0]
        folder = m.find(dirname, exclude_deleted=True)
        if folder is None:
            m.create_folder(dirname)
            folder = m.find(dirname, exclude_deleted=True)
        pbar = utils.progress_bar(len(os.listdir(f"./download/{username}"))+1)
        for file in os.listdir(f"./download/{username}"):
            if not m.find(file, exclude_deleted=True):
                m.upload(f"./download/{username}/{file}", folder[0])
            else:
                print(f"[!] Already exists (file:{file})", " "*50)
            print(f"[*] Upload {pbar.update()}", end='\r')
            os.remove(f"./download/{username}/{file}")
        print(f"\r[+] Uploaded {pbar.update()} ")

    print(f"[+] Profile {username} scanned\n")
