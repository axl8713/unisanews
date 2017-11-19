'''
Created on Nov 15, 2015

@author: aleric
'''
import logging
import requests
import pytz
import re
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer
from entities import NewsItem
import dateparser


class UnisaNewsCrawler(object):
    LAST_PAGE = 3
    MAX_PAGES = 3

    def crawl(self):

        pages = self._spider()
        for page in pages:
            for NewsItem in self._parse(page):
                yield NewsItem

    def _spider(self):

        start_url = "http://web.unisa.it/home/news"
        older_page_index = self.LAST_PAGE
        newer_page_index = self.LAST_PAGE - self.MAX_PAGES

        for page_index in range(newer_page_index, older_page_index + 1):
            page_url = start_url + "?page=" + str(page_index)

            logging.info("start crawling " + page_url)

            response = requests.get(page_url, headers={'Content-Type': 'text/html', 'Accept-Encoding': None})

            yield response.content

    def _parse(self, page):

        soup = BeautifulSoup(page, "lxml", parse_only=SoupStrainer("ul", class_="event-list event-left"))
        lis = soup.find_all("li")

        for li in lis:
            yield self._scrape_news_div(li.div)

    def _scrape_news_div(self, div):

        unisa_base_url = "http://web.unisa.it"

        item = NewsItem()
        item.title = unicode(div.h4.a.string)
        item.link = unicode(unisa_base_url + div.h4.a.get("href"))
        news_description = div.p.string
        if news_description is not None:
            item.description = unicode(news_description)
        else:
            # if there's no description, set it with title
            item.description = item.title
            item.title = unicode(div.h5.small.string)
        item.pub_date = self._parse_pub_date(unicode(div.find_all("p")[1].small.string))
        item.fetch_date = datetime.utcnow()

        return item

    def _parse_pub_date(self, pub_date):
        match = re.match(r'Pubblicato\s+il\s+(\d+\s+\w+\s+\d{2,4})', pub_date)
        if match:
            parsed_date = dateparser.parse(match.group(1), ["%d %B %Y"], ["it"])
            utc_date = self._localize_date_to_rome_tz(parsed_date)
            return utc_date
        else:
            return self._localize_date_to_rome_tz(datetime.now())

    def _localize_date_to_rome_tz(self, parsed_date):
        return pytz.timezone("Europe/Rome").localize(parsed_date)
