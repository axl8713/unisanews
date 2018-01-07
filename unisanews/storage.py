"""
Created on Nov 15, 2015

@author: aleric
"""
import logging
import MySQLdb
from entities import NewsItem
from flask import current_app, g

logging.basicConfig(level=logging.DEBUG)


class UnisaNewsMySqlStorage(object):
    _query_select_items = "SELECT title, link, fetch_date, pub_date, description FROM news_item ORDER BY pub_date DESC"

    _query_insert_item = ("INSERT INTO news_item (title, link, fetch_date, pub_date, description) "
                          "VALUES (%s, %s, %s, %s, %s)")

    _query_select_newer_item = ("SELECT newest_item.id FROM "
                                "news_item, "
                                "(SELECT * FROM news_item ORDER BY pub_date DESC limit 1) as newest_item "
                                "WHERE "
                                "newest_item.pub_date > %s "
                                "OR "
                                "news_item.link = %s")

    _query_delete_older_items = ("DELETE FROM news_item "
                                 "WHERE id IN ("
                                 "SELECT item_to_be_deleted.id FROM ("
                                 "SELECT id "
                                 "FROM news_item "
                                 "ORDER BY pub_date DESC "
                                 "LIMIT 9999 OFFSET %s"
                                 ") AS item_to_be_deleted"
                                 ")")
    _ITEMS_TO_KEEP = 50

    @staticmethod
    def get_connection():
        # https://stackoverflow.com/a/32017603/1291616
        return MySQLdb.connect(
            host=current_app.config["DATABASE_URL"],
            port=current_app.config["DATABASE_PORT"],
            user=current_app.config["DATABASE_USER"],
            passwd=current_app.config["DATABASE_PASSWORD"],
            db=current_app.config["DATABASE_NAME"],
            charset='utf8')

    def _connect(self):
        if not hasattr(g, 'unisanews_db'):
            g.unisanews_db = self.get_connection()
        return g.unisanews_db

    def retrieve_news_items_from_storage(self):

        connection = self._connect()
        cursor = connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        cursor.execute(self._query_select_items)
        rows = cursor.fetchall()
        for row in rows:
            item = NewsItem()
            item.title = row["title"]
            item.link = row["link"]
            item.fetch_date = row["fetch_date"]
            item.pub_date = row["pub_date"]
            item.description = row["description"]
            yield item

        cursor.close()
        connection.close()

    def delete_older_news_items(self, cursor):

        cursor.execute(self._query_delete_older_items, (self._ITEMS_TO_KEEP,))
        logging.debug("deleted " + str(cursor.rowcount) + " old items")

    def update_news_items_storage(self, news_items):

        connection = self._connect()
        cursor = connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        for news_item in news_items:

            logging.info(">>>>> " + news_item.title)

            if self._is_item_to_be_saved(cursor, news_item):
                logging.info("unique or newer, saving item")
                self._save_news_item(cursor, news_item)
                yield news_item
            else:
                logging.info("exists or older, skipping item")

        logging.info("deleting older news items...")
        self.delete_older_news_items(cursor)

        logging.debug("committing changes to storage")
        connection.commit()

        cursor.close()
        connection.close()

    def _is_item_to_be_saved(self, cursor, news_item):
        cursor.execute(self._query_select_newer_item, (news_item.pub_date, news_item.link))
        return cursor.rowcount == 0

    def _save_news_item(self, cursor, news_item):
        logging.debug("adding insert query to transaction")
        cursor.execute(
            self._query_insert_item,
            (news_item.title, news_item.link, news_item.fetch_date, news_item.pub_date, news_item.description)
        )
