"""
Created on May 17, 2014

@author: aleric
"""
import logging
import time

import tweepy
from flask import current_app


class Tuitter(object):
    MAX_TWEET_LENGTH = 280  # characters
    URL_SHORT_LENGTH = 23  # characters
    TWEET_DELAY = 30  # seconds

    def tweet_news(self, news_items):

        tweet_sending = current_app.config["TWEET_SENDING"]

        for news_item in news_items:

            logging.info("tweeting")
            tweet_text = self._compose_tweet(news_item)

            if tweet_sending:
                self._send_tweet(tweet_text)
                logging.info("waiting " + str(self.TWEET_DELAY) + " sec before next tweet (if any)...")
                time.sleep(self.TWEET_DELAY)
            else:
                logging.debug("TWEET! -> " + tweet_text)

    def _send_tweet(self, tweet_text):
        auth = tweepy.OAuthHandler(current_app.config["TWITTER_API_KEY"], current_app.config["TWITTER_API_SECRET"])
        auth.set_access_token(current_app.config["TWITTER_ACCESS_TOKEN"], current_app.config["TWITTER_TOKEN_SECRET"])
        api = tweepy.API(auth)
        api.update_status(status=tweet_text)

    def _compose_tweet(self, item):
        tweet_text = item.title + " - " + item.description.strip() + " "
        tweet_length = len(tweet_text) + self.URL_SHORT_LENGTH
        if tweet_length > self.MAX_TWEET_LENGTH:
            tweet_text = self._shrink_text(tweet_text)
        tweet_text = tweet_text + item.link
        return tweet_text

    def _shrink_text(self, tweet_text):
        delta = (len(tweet_text) + self.URL_SHORT_LENGTH) - self.MAX_TWEET_LENGTH

        print (len(tweet_text))
        print delta

        return tweet_text[:-delta - 3].strip() + u'\u2026' + " "
