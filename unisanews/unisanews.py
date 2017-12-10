import os
from flask import Flask, render_template, send_from_directory, make_response
from crawler import UnisaNewsCrawler
from storage import UnisaNewsMySqlStorage

app = Flask(__name__, instance_relative_config=True)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , unisanews.py

# Questa e' la configurazione di default
app.config.update(dict(
    DATABASE_NAME='unisanews'
))

# qui si carica la configurazione di default oppure quella che ha nel nome del file il valore della variabile d'ambiente
# UNISANEWS_CONFIGURATION nella cartella instance (instance folder di flask)
configuration = os.getenv('UNISANEWS_CONFIGURATION', 'default')
app.config.from_pyfile('unisanews_' + configuration + '.cfg')


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

    response = make_response(render_template('rss.xml', items=saved_items))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# per test in locale
if __name__ == "__main__":
    app.run(host='0.0.0.0')
