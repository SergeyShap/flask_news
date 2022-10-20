import json
import logging
import urllib
import urllib.request as urllib2
import feedparser
from flask import Flask
from flask import render_template
from flask import request
from config import CURRENCY_TOKEN, WEATHER_TOKEN

app = Flask(__name__)

def setup_logger(name):
    """ Setup logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent logging from propagating to the root loggger
        logger.propagate = 0
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter('%(asctime)s \t%(levelname)s \t%(processName)s \t%(message)s')
        console.setFormatter
    return logger

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id={}"

RSS_FEEDS = {'simplecast': 'https://feeds.simplecast.com/54nAGcIl',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640',
             }

DEFAULT = {'publication': 'fox',
           'city': 'London,UK',
           'currency_from': 'GBP',
           'currency_to': 'USD'}

@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULT['publication']
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULT['city']
    weather = get_weather(city)
    # get customized currency based on user input or default
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULT['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULT['currency_to']
    rate = get_rate(currency_from, currency_to)
    logger.info(f"{rate}")
    return render_template("home.html",
                           articles=articles,
                           weather=weather,
                           currency_from=currency_from,
                           currency_to=currency_to,
                           rate=rate,
                           )


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULT["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    # logger.info(f"{feed['entries']}")
    return feed['entries']


def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query, WEATHER_TOKEN)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   'country': parsed['sys']['country'],
                   }
    return weather

def get_rate(frm, to):
    url = CURRENCY_URL.format(CURRENCY_TOKEN)
    all_currency = urllib2.urlopen(url).read()

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate/frm_rate

if __name__ == '__main__':
    logger = setup_logger("flask_news")
    logger.setLevel(logging.INFO)
    app.run(port=5000, debug=True)
