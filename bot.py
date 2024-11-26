#!/usr/bin/env python3
# Simple Discord SelfBot
# Created By Viloid ( github.com/vsec7 )
# Use At Your Own Risk

import requests, random, sys, yaml, time
import os
import threading
from flask import Flask

# Flask app setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# Start Flask server in a separate thread
thread = threading.Thread(target=run_server)
thread.start()

# Discord bot functionality
class Discord:
    def __init__(self, t):
        self.base = "https://discord.com/api/v9"
        self.auth = { 'authorization': t }
        
    def getMe(self):
        return requests.get(self.base + "/users/@me", headers=self.auth).json()
        
    def getMessage(self, cid, l):
        return requests.get(f"{self.base}/channels/{cid}/messages?limit={l}", headers=self.auth).json()
        
    def sendMessage(self, cid, txt):    
        return requests.post(f"{self.base}/channels/{cid}/messages", headers=self.auth, json={ 'content': txt }).json()

    def replyMessage(self, cid, mid, txt):    
        return requests.post(f"{self.base}/channels/{cid}/messages", headers=self.auth, json={ 'content': txt, 'message_reference': { 'message_id': str(mid) } }).json()

    def deleteMessage(self, cid, mid):
        return requests.delete(f"{self.base}/channels/{cid}/messages/{mid}", headers=self.auth)

def quote():
    u = requests.get("https://raw.githubusercontent.com/lakuapik/quotes-indonesia/master/raw/quotes.min.json").json()
    return random.choice(list(u))['quote']

def simsimi(lc, txt):
    u = requests.post("https://api.simsimi.vn/v1/simtalk", data={ 'lc': lc, 'text': txt}).json()
    return u['message']

def main():
    with open('config.yaml') as cfg:
        conf = yaml.load(cfg, Loader=yaml.FullLoader)

    if not conf['BOT_TOKEN']:
        print("[!] Please provide discord token at config.yaml!")
        sys.exit()

    if not conf['CHANNEL_ID']:
        print("[!] Please provide channel id at config.yaml!")
        sys.exit()

    mode = conf.get('MODE', 'quote')
    simi_lc = conf.get('SIMSIMI_LANG', 'id')
    delay = conf.get('DELAY', 10)
    del_after = conf.get('DEL_AFTER', False)
    repost_last = conf.get('REPOST_LAST_CHAT', 100)
    
    while True:
        for token in conf['BOT_TOKEN']:
            try:
                for chan in conf['CHANNEL_ID']:
                    Bot = Discord(token)
                    me = f"{Bot.getMe()['username']}#{Bot.getMe()['discriminator']}"

                    if mode == "quote":
                        q = quote()
                        send = Bot.sendMessage(chan, q)
                        print(f"[{me}][{chan}][QUOTE] {q}")
                        if del_after:
                            Bot.deleteMessage(chan, send['id'])
                            print(f"[{me}][DELETE] {send['id']}")

                    elif mode == "repost":
                        res = Bot.getMessage(chan, random.randint(1, repost_last))
                        getlast = list(reversed(res))[0]
                        send = Bot.sendMessage(chan, getlast['content'])
                        print(f"[{me}][{chan}][REPOST] {getlast['content']}")
                        if del_after:
                            Bot.deleteMessage(chan, send['id'])
                            print(f"[{me}][DELETE] {send['id']}")

                    elif mode == "simsimi":
                        res = Bot.getMessage(chan, 1)
                        getlast = list(reversed(res))[0]
                        simi = simsimi(simi_lc, getlast['content'])

                        if conf.get('REPLY', False):
                            send = Bot.replyMessage(chan, getlast['id'], simi)
                            print(f"[{me}][{chan}][SIMSIMI] {simi}")
                        else:
                            send = Bot.sendMessage(chan, simi)
                            print(f"[{me}][{chan}][SIMSIMI] {simi}")

                        if del_after:
                            Bot.deleteMessage(chan, send['id'])
                            print(f"[{me}][DELETE] {send['id']}")

                    elif mode == "custom":
                        c = random.choice(open("custom.txt").readlines())
                        send = Bot.sendMessage(chan, c.strip())
                        print(f"[{me}][{chan}][CUSTOM] {c}")
                        if del_after:
                            Bot.deleteMessage(chan, send['id'])
                            print(f"[{me}][DELETE] {send['id']}")

            except Exception as e:
                print(f"[Error] {token} : {str(e)}")
        
        print(f"-------[ Delay for {delay} seconds ]-------")
        time.sleep(delay)

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(f"{type(err).__name__} : {err}")
