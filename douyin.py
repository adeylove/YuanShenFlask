import requests as adey
import re
import random
from plyer import notification
import wget
import json
import os
import sys

header = {'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet'}
Data = {"id": "", "url": "", "XBogus": "", "param": "", "msToken": "",
        "ttwid": "", "new": ""}
bd_ticket_guard_client_data = "eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVKUDZzbjNLRlFBNUROSEcyK2F4bXAwNG5cclxud1hBSTZDU1IyZW1sVUE5QTZ4aGQzbVlPUlI4NVRLZ2tXd1FJSmp3Nyszdnc0Z2NNRG5iOTRoS3MvSjFJc3FBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnVmJkWTI0c0RYS0c0S2h3WlBmOHpxVDRBU0ROamNUb2FFRi9MQnd2QS8xSUNcclxuSURiVmZCUk1PQVB5cWJkcytld1QwSDZqdDg1czZZTVNVZEo5Z2dmOWlmeTBcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9"
odin_tt = "324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69;"


def Web_original(tiktok_url):
    original_adey = adey.get(url=tiktok_url, headers=header)
    Data["url"] = original_adey.url


def Web_processor():
    Web_original(tiktok_url=i)
    search = re.findall(r"[0-9]{19}", Data["url"])[0]
    Data['id'] = search


def WebXBogus():
    Web_processor()
    url = "http://127.0.0.1:520/xbogus"
    o = f'https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={Data["id"]}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
    JsonData = {
        "url": o,
        "user_agent": "TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet"
    }
    bot = adey.post(url=url, headers=header, json=JsonData).json()
    Data["XBogus"] = bot["X-Bogus"]
    Data["param"] = bot["param"]


def msToken(random_length=107):
    WebXBogus()
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
    length = len(base_str) - 1
    for _ in range(random_length):
        random_str += base_str[random.randint(0, length)]
    Data["msToken"] = random_str


def odin_tto():
    msToken()
    json = {"region": "cn", "aid": 1768, "needFid": 'false', "service": "www.ixigua.com",
            "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": "True"}
    a = adey.post(url="https://ttwid.bytedance.com/ttwid/union/register/", headers=header, json=json)
    b = a.headers["Set-Cookie"]
    c = b.split(";")[0]
    odin_tt_str = re.sub("ttwid=", "", c)
    Data["ttwid"] = odin_tt_str


def Webapi():
    odin_tto()
    api_header = {
        "Accept": "* / *",
        "Referer": "https: // www.douyin.com /",
        'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
        "cookie": f'msToken={Data["msToken"]} ; odin_tt={odin_tt} ;ttwid={Data["ttwid"]} ;bd_ticket_guard_client_data={bd_ticket_guard_client_data}'}
    url = Data["param"]
    own = adey.get(url=url, headers=api_header).json()
    """
    DATA = json.dumps(own, ensure_ascii=False, sort_keys=True)
    print(DATA)
    """
    return own


def WebDownload():
    getting = Webapi()
    name = ""
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    for number in range(11):
        o = int(random.randint(0, 61))
        name += base_str[o]
    try:
        os.mkdir(name)
        Background_music = getting["aweme_detail"]["music"]["play_url"]["url_list"][0]
        Background_music_Download = wget.download(Background_music, out=os.path.join(name, f"{name}.m4a"))
        Video = getting["aweme_detail"]["video"]["play_addr_h264"]["url_list"][3]
        Video_Download = wget.download(Video, out=os.path.join(name,f"{name}.mp4"))
        notification.notify(title='DouyinScan', message=f'{name}.mp4', app_icon="me.ico", timeout=10)
    except:
        print("Python Error")


if __name__ == '__main__':
    i = sys.argv[1]
    WebDownload()
