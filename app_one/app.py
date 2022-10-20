import json
import logging
import urllib
import urllib.request as urllib2
import feedparser
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=aa419bc879713a750647c3aa4b13e335"

RSS_FEEDS = {'simplecast': 'https://feeds.simplecast.com/54nAGcIl',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             }

DEFAULT = {'publication': 'fox',
            'city': 'London,UK'}

@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULT['publication']
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    # logging.INFO("%s", city)
    if not city:
        city = DEFAULT['city']
    weather = get_weather(city)
    return render_template("home.html", articles=articles, weather=weather)


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULT["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   }
    return weather

if __name__ == '__main__':
    app.run(port=5000, debug=True)
