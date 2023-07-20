import json
import urllib.parse
import time
import random
import re
import string
import execjs
from reahead import requests_head
from hashlib import md5
from datetime import timedelta
import requests as adey
from flask_sqlalchemy import SQLAlchemy as SQL
from flask import Flask, render_template, session, request, jsonify

# 读取数据库配置文件
Json_Configuration = open('Configuration.json', 'r', encoding='utf-8').read()
Configuration = json.loads(Json_Configuration)['config']
Sever = json.loads(Json_Configuration)['sever']

# 实例化Flask类.创建app对象
app = Flask(__name__)

# 创建数据库对象
app.config[
    "SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{Configuration['Username']}:{Configuration['Password']}@{Configuration['Host']}:{Configuration['Port']}/{Configuration['Database']}?charset=utf8mb4"

# 设置Session密钥
app.secret_key = 'AD5D4999682BC0B7D3684EC61905805F'

# 设置session过期时间
app.permanent_session_lifetime = timedelta(hours=1)

# 创建数据库连接对象
db = SQL(app)


# MD5加密函数
def obj(data):
    md5_obj = md5()
    md5_obj.update(data.encode('utf-8'))
    return md5_obj.hexdigest()


# User模型
class Information(db.Model):
    __tablename__ = 'information'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)


# 原神解析调用函数：
data = {}
user_data = {}
cardpool, cardpool_id, end_id = [], [], []


def random_text(number: int) -> str:
    return ''.join(random.sample(string.ascii_lowercase + string.digits, number))


def ret_requests0(key):
    headers = {'User-Agent': f'{requests_head()}'}
    url = f'https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?region={user_data["region"]}&win_mode=fullscreen&authkey_ver=1&sign_type=2&auth_appid=webview_gacha&init_type=301&gacha_id={user_data["game_uid"]}&lang=zh-cn&device_type=mobile&game_version=CNRELiOS3.0.0_R10283122_S10446836_D10316937&plat_type=ios&authkey={key}&game_biz=hk4e_cn&gacha_type=301&page=1&size=5&end_id=0'
    get = adey.get(url=url, headers=headers).json()['data']['list']
    for data in get:
        cardpool_id.append(data['id'])
        cardpool.append(data['name'])
    end_id.append(cardpool_id[4])


def ret_requests1(key):
    name = 'True'
    headers = {'User-Agent': f'{requests_head()}'}
    url = f'https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?region={user_data["region"]}&win_mode=fullscreen&authkey_ver=1&sign_type=2&auth_appid=webview_gacha&init_type=301&gacha_id={user_data["game_uid"]}&lang=zh-cn&device_type=mobile&game_version=CNRELiOS3.0.0_R10283122_S10446836_D10316937&plat_type=ios&authkey={key}&&game_biz=hk4e_cn&gacha_type=301&page=1&size=20&end_id={end_id[0]}'
    get = adey.get(url=url, headers=headers).json()['data']['list']
    if not get:
        name = "False"
    end_id.clear()
    for data in get:
        cardpool_id.append(data['id'])
        cardpool.append(data['name'])
    end_id.append(cardpool_id[len(cardpool_id) - 1])
    return name


# 网站根路由创建
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "GET":
        if session.get('username') is None and session.get('token') is None:
            return render_template("index.html", username='你还未登录!')
        else:
            session_username = session.get('username')
            session_token = session.get("token")
            query = Information.query.filter_by(username=session_username).first()
            if session_username == query.username and session_token == obj(query.username + obj(query.password)):
                return render_template('index.html', username=session_username)
            else:
                return render_template("index.html", username='你还未登录!')
    elif request.method == "POST":
        cookie = request.form.get("cookie")
        headers = {'User-Agent': 'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01', "cookie": cookie}
        # 获取UID
        url = 'https://webapi.account.mihoyo.com/Api/login_by_cookie?t='
        account_info = adey.get(url + str(int(time.time() * 1000)), headers=headers).json()
        login_uid = account_info['data']['account_info']['account_id']
        data['app_uid'] = login_uid
        login_token = account_info['data']['account_info']['weblogin_token']
        data['web_token'] = login_token
        # 处理Cookie
        url = f'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={data["web_token"]}&token_types=3&uid={data["app_uid"]}'
        ret = adey.get(url=url, headers=headers).json()['data']['list']
        cookie_str = f"stuid={data['app_uid']}; "
        cookie_str1 = ""
        for i in ret:
            cookie_str1 += f'{i["name"]}={i["token"]}; '
        cookie_str += cookie_str1
        cookie_str += cookie
        data['cookie'] = cookie_str
        # 添加用户数据：
        header = {'User-Agent': 'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.7.62 Version/11.01',
                  "cookie": data['cookie']}
        url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn'
        ret = adey.get(url=url, headers=header).json()['data']['list']
        user_ = ret[0]
        user_data['name'] = user_['nickname']
        user_data["game_biz"] = user_['game_biz']
        user_data["game_uid"] = user_["game_uid"]
        user_data["region"] = user_['region']
        user_data['level'] = user_['level']
        user_data['region_name'] = user_['region_name']
        # DS算法
        salt = 'ulInCDohgEs557j0VsPDYnQaaz6KJcv5'
        now = str(int(time.time()))
        text = random_text(6)
        c = obj("salt=" + salt + "&t=" + now + "&r=" + text)
        ds = f"{now},{text},{c}"
        headers = {'Content-Type': 'application/json; charset=utf-8',
                   'Host': 'api-takumi.mihoyo.com',
                   'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://webstatic.mihoyo.com',
                   'x-rpc-app_version': '2.28.1',
                   'x-rpc-client_type': '5',
                   'x-rpc-device_id': 'CBEC8312-AA77-489E-AE8A-8D498DE24E90',
                   'x-requested-with': 'com.mihoyo.hyperion',
                   'DS': ds,
                   'Cookie': data['cookie'],
                   }
        json = {
            "auth_appid": 'webview_gacha',
            'game_biz': user_data['game_biz'],
            'game_uid': user_data['game_uid'],
            "region": user_data['region']
        }
        url = 'https://api-takumi.mihoyo.com/binding/api/genAuthKey'
        ret = adey.post(url=url, headers=headers, json=json).json()['data']['authkey']
        # 获取authkey
        key = urllib.parse.quote(ret)
        ret_requests0(key)
        while True:
            sudo = ret_requests1(key)
            if sudo == "False":
                break
    return f'你一共抽了{len(cardpool)}'


# 登录页面HTML
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if session.get('username') is None and session.get('token') is None:
            return render_template('login.html')
        else:
            session_username = session.get('username')
            session_token = session.get("token")
            query = Information.query.filter_by(username=session_username).first()
            if session_username == query.username and session_token == obj(query.username + obj(query.password)):
                return f'<script>alert("你已登录！{session_username}");</script>'
            else:
                return render_template('login.html')
    elif request.method == "POST":
        username = request.form.get('username')
        passwd = request.form.get('password')
        data = Information.query.filter_by(username=username, password=passwd).first()
        if data is None:
            return '<script>alert("登录失败！");</script>'
        else:
            session['username'] = username
            session['token'] = obj(username + obj(passwd))
            return '<script language="javascript" type="text/javascript">window.location.href="/";</script>'


# 注册页面HTML
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        username = request.form.get('username')
        passwd = request.form.get('password')
        email = request.form.get('email')
        data = Information.query.filter_by(username=username).first()
        if data is None:
            info = Information()
            info.username = username
            info.password = passwd
            info.email = email
            db.session.add(info)
            db.session.commit()
            return '<script language="javascript" type="text/javascript">window.location.href="/login";</script>'
        else:
            return '用户已经存在！'


# Session清理页面:
@app.route('/logout')
def logout():
    session.clear()
    return '<script language="javascript" type="text/javascript">window.location.href="/";</script>'


# 抖音X-bogus
@app.route('/xbogus', methods=['POST'])
def generate_request_params():
    data = request.get_json()
    url = data.get('url')
    user_agent = data.get('user_agent')
    query = urllib.parse.urlparse(url).query
    xbogus = execjs.compile(open('static/javascript/X-Bogus.js').read()).call('sign', query, user_agent)
    new_url = url + "&X-Bogus=" + xbogus
    response_data = {
        "param": new_url,
        "X-Bogus": xbogus
    }
    return jsonify(response_data)


# 抖音解析HTML
@app.route('/douyin', methods=["POST", "GET"])
def douyin():
    if request.method == "POST":
        url = request.form.get('tiktok')
        header = {'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet'}
        Data = {"id": "", "url": "", "XBogus": "", "param": "", "msToken": "", "ttwid": "", "new": ""}
        bd_ticket_guard_client_data = "eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVKUDZzbjNLRlFBNUROSEcyK2F4bXAwNG5cclxud1hBSTZDU1IyZW1sVUE5QTZ4aGQzbVlPUlI4NVRLZ2tXd1FJSmp3Nyszdnc0Z2NNRG5iOTRoS3MvSjFJc3FBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnVmJkWTI0c0RYS0c0S2h3WlBmOHpxVDRBU0ROamNUb2FFRi9MQnd2QS8xSUNcclxuSURiVmZCUk1PQVB5cWJkcytld1QwSDZqdDg1czZZTVNVZEo5Z2dmOWlmeTBcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9"
        odin_tt = "324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69;"
        original_adey = adey.get(url=url, headers=header)
        Data["url"] = original_adey.url
        search = re.findall(r"[0-9]{19}", Data["url"])[0]
        Data['id'] = search
        url = f"{Sever['url']}:{Sever['port']}/xbogus"
        o = f'https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={Data["id"]}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
        JsonData = {
            "url": o,
            "user_agent": "TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet"
        }
        bot = adey.post(url=url, headers=header, json=JsonData).json()
        Data["XBogus"] = bot["X-Bogus"]
        Data["param"] = bot["param"]
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        random_length = 107
        for _ in range(random_length):
            random_str += base_str[random.randint(0, length)]
        Data["msToken"] = random_str
        json = {"region": "cn", "aid": 1768, "needFid": 'false', "service": "www.ixigua.com",
                "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": "True"}
        a = adey.post(url="https://ttwid.bytedance.com/ttwid/union/register/", headers=header, json=json)
        b = a.headers["Set-Cookie"]
        c = b.split(";")[0]
        odin_tt_str = re.sub("ttwid=", "", c)
        Data["ttwid"] = odin_tt_str
        api_header = {
            "Accept": "* / *",
            "Referer": "https: // www.douyin.com /",
            'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
            "cookie": f'msToken={Data["msToken"]} ; odin_tt={odin_tt} ;ttwid={Data["ttwid"]} ;bd_ticket_guard_client_data={bd_ticket_guard_client_data}'}
        url = Data["param"]
        own = adey.get(url=url, headers=api_header).json()
        return f'视频地址：{own["aweme_detail"]["video"]["play_addr_h264"]["url_list"][3]}'
    else:
        if session.get('username') is None and session.get('token') is None:
            return render_template('douyin.html', username='你还未登录!')
        else:
            session_username = session.get('username')
            session_token = session.get("token")
            query = Information.query.filter_by(username=session_username).first()
            if session_username == query.username and session_token == obj(query.username + obj(query.password)):
                return render_template('douyin.html', username=session_username)
            else:
                return render_template("douyin.html", username='你还未登录!')


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(port=9999, debug=True)
