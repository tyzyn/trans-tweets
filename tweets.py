from argparse import ArgumentParser
from datetime import datetime
import mysql.connector
import tweepy
import time
import json

parser = ArgumentParser()
parser.add_argument("-c", "--credentials", dest="credentials", default="creds1.txt")
parser.add_argument("-t", "--track", dest="track", default="track1.txt")
parser.add_argument("-u", "--user", dest="username", default="tyson")
parser.add_argument("-p", "--password", dest="password")

args = parser.parse_args()

db = mysql.connector.connect(
    host="localhost",
    user=args.username,
    password=args.password,
    database="tweets"
)

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, api, db):
        self.api = api
        self.db = db
        self.cursor = self.db.cursor()

    def on_status(self, tweet):
        j = tweet._json

        if j["truncated"]:
            text = j["extended_tweet"]["full_text"]
        else:
            text = j["text"]

        text = text.encode("ascii", "ignore").decode()
        user = j["user"]["screen_name"]

        print(user)
        print(len(text))
        sql = "INSERT INTO trans (time, user, text) VALUES (%s, %s, %s)"
        val = (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), user, text)
        self.cursor.execute(sql, val)
        self.db.commit()

#grab credentials from txt file
with open("creds/"+args.credentials, "r") as fin:
    CREDENTIALS = [line.strip() for line in fin.readlines()]

CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET = CREDENTIALS

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

with open("track/"+args.track, "r") as fin:
    track = [line.strip() for line in fin.readlines()]

print(track)
stream = MyStreamListener(api, db)
stream = tweepy.Stream(api.auth, stream)
stream.filter(track=track, languages=["en"])
