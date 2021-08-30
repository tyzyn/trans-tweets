from argparse import ArgumentParser
from datetime import datetime
import tweepy
import time
import json

parser = ArgumentParser()
parser.add_argument("-c", "--credentials", dest="credentials", default="creds1.txt")
parser.add_argument("-t", "--track", dest="track", default="track1.txt")
parser.add_argument("-u", "--user", dest="username", default="tyson")
parser.add_argument("-p", "--password", dest="password")

args = parser.parse_args()

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api

    def on_status(self, tweet):
        j = tweet._json
        created_at = datetime.strftime(datetime.strptime(j['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
        dt = created_at.split()[0].replace('-', '') + created_at.split()[1].split(':')[0]
        with open("data/"+args.track.replace(".txt","")+"_"+dt+".jsonl", "a+") as fout:
            fout.write(json.dumps(j)+"\n")
        print("Tweet by", j['user']['screen_name'], "at", created_at)

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
stream = MyStreamListener(api)
stream = tweepy.Stream(api.auth, stream)
stream.filter(track=track, languages=["en"])
