"""
Created on Nov 15, 2015

@author: aleric
"""
import logging
import re
import requests
import dateparser
from bs4 import BeautifulSoup, SoupStrainer
from pytz import timezone
from datetime import datetime
from entities import NewsItem
from xml.sax.saxutils import escape


class UnisaNewsCrawler(object):
    UNISA_BASE_URL = "http://web.unisa.it"

    PYTZ_ROME_TIMEZONE = timezone("Europe/Rome")

    LAST_PAGE = 3
    MAX_PAGES = 3

    def crawl(self):

        pages = self._spider()
        for page in pages:
            for news_item in self._parse(page):
                yield news_item

    def _spider(self):

        start_url = "http://web.unisa.it/home/news"
        older_page_index = self.LAST_PAGE
        newer_page_index = self.LAST_PAGE - self.MAX_PAGES

        for page_index in range(older_page_index, newer_page_index, -1):
            page_url = start_url + "?page=" + str(page_index)

            logging.info("start crawling " + page_url)

            response = requests.get(page_url, headers={'Content-Type': 'text/html', 'Accept-Encoding': None})

            yield response.content

    def _parse(self, page):

        soup = BeautifulSoup(page, "lxml", parse_only=SoupStrainer("ul", class_="event-list event-left"))
        lis = soup.find_all("li")
        lis_from_oldest = reversed(lis)

        for li in lis_from_oldest:
            yield self._scrape_news_div(li.div)

    def _scrape_news_div(self, div):

        item = NewsItem()
        item.title = escape(div.h4.a.string)
        item.link = escape(self.UNISA_BASE_URL + div.h4.a.get("href"))
        news_description = div.p.string

        if news_description is not None:
            item.description = escape(news_description)
        else:
            # if there's no description, set it with title
            item.description = item.title
            # and set title with category
            item.title = escape(div.h5.small.string)

        item.pub_date = self._parse_pub_date(escape(div.find_all("p")[1].small.string))
        item.fetch_date = datetime.now(self.PYTZ_ROME_TIMEZONE)

        return item

    def _parse_pub_date(self, pub_date):
        match = re.match(r'Pubblicato\s+il\s+(\d+\s+\w+\s+\d{2,4})', pub_date)
        if match:
            return dateparser.parse(match.group(1), ["%d %B %Y"], ["it"])
        else:
            return datetime.now(self.PYTZ_ROME_TIMEZONE)
