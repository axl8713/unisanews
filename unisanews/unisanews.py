import os
import logging
from flask import Flask, render_template, send_from_directory, make_response, g
from crawler import UnisaNewsCrawler
from storage import UnisaNewsMySqlStorage
from tuitter import Tuitter

app = Flask(__name__, instance_relative_config=True)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file, unisanews.py

# http://flask.pocoo.org/docs/0.10/config/#instance-folders
app.config.update(dict(
    DATABASE_NAME='unisanews'
))
configuration = os.getenv('UNISANEWS_CONFIGURATION', 'default')
app.config.from_pyfile('unisanews_' + configuration + '.cfg')


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'unisanews_db'):
        if g.unisanews_db.open:
            g.unisanews_db.close()


@app.template_filter('rfc822Date')
def format_date_to_rfc822(date):
    return date.strftime("%a, %d %b %Y %H:%M:%S %z")


@app.route('/unisa_feed.rss')
def rss_feed():
    news_items = UnisaNewsMySqlStorage().retrieve_news_items_from_storage()
    response = make_response(render_template('rss.xml', items=news_items))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


@app.route('/update_feed')
def update_feed():
    news_items = UnisaNewsCrawler().crawl()
    saved_items = UnisaNewsMySqlStorage().update_news_items_storage(news_items)
    Tuitter().tweet_news(saved_items)

    response = make_response(render_template('rss.xml', items=saved_items))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def init_db():
    with app.app_context():
        db = UnisaNewsMySqlStorage.get_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().execute(f.read())
    db.commit()


if __name__ == "__main__":
    init_db()
    logging.debug('Initialized the database.')
    app.run(host='0.0.0.0')
