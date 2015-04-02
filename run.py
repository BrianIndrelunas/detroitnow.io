# Python imports
from __future__ import print_function
import json
import os.path
import logging
from datetime import datetime, timedelta

# Tornado imports
from tornado import gen, ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, Application, asynchronous
from tornado.options import define, options, parse_command_line, \
                                parse_config_file

# Local imports
from beats import geo_point, engage, popular, active, authors, stats, \
                    viewers, referral

define("port", default=8888, help="run on the given port", type=int)
define("API", default="317a25eccba186e0f6b558f45214c0e7",
        help="chartbeat api key", type=str)
define("chartbeat_url", default="http://api.chartbeat.com",
        help="chartbeat base URL", type=str)
define("sites", default=("avc.com"), help="chartbeat sites", type=tuple)
define("debug", default=True, help="Debug state", type=bool)

base_dir = os.path.dirname(__file__)
parse_config_file(os.path.join(base_dir, "settings.cfg"))

BEATS = [geo_point,
         engage,
         popular,
         active,
         authors,
         stats,
         viewers,
         referral]


class Main(RequestHandler):
    @asynchronous
    def get(self):
        self.render("index.html")


class GeoPoint(RequestHandler):
    @asynchronous
    def get(self):
        with open("templates/mustache/geo_point.mustache") as fp:
            template = fp.read()
        print(template)
        self.render("geo_point.html", template=template)


class Engage(RequestHandler):
    @asynchronous
    def get(self):
        self.render("engage.html")


class Active(RequestHandler):
    @asynchronous
    def get(self):
        self.render("active.html")


class Viewers(RequestHandler):
    @asynchronous
    def get(self):
        self.render("viewers.html")


class Recirculation(RequestHandler):
    @asynchronous
    def get(self):
        self.render("recirculation.html")


class Authors(RequestHandler):
    @asynchronous
    def get(self):
        self.render("authors.html")


class Referral(RequestHandler):
    @asynchronous
    def get(self):
        with open("templates/mustache/referral.mustache") as fp:
            template = fp.read()
        self.render("referral.html", template=template)


class Popular(RequestHandler):
    @asynchronous
    def get(self):
        with open("templates/mustache/popular_article.mustache") as fp:
            template = fp.read()
        self.render("popular.html", template=template)


class Stats(RequestHandler):
    @asynchronous
    def get(self):
        with open("templates/mustache/stats_table.mustache") as fp:
            table_template = fp.read()
        with open("templates/mustache/stats_table_row.mustache") as fp:
            table_row_template = fp.read()
        self.render("stats.html", table_template=table_template, table_row_template=table_row_template)

class TigersXtra(RequestHandler):
    @asynchronous
    def get(self):
        self.render('tigers-xtra.html', ios_link='http://j.mp/tigersios',
                        android_link='http://j.mp/tigersand')

@gen.coroutine
def chartbeat_heartbeat():
    """ Infinite loop that requests all chartbeat data
    This function detects whether or not there are active connections
    to any of our dashboards via a websocket and then determines what
    data to request from Chartbeat."""
    loop = ioloop.IOLoop.current()
    http_client = AsyncHTTPClient()
    while True:
        logging.info("Chartbeat heartbeat at {0}".format(datetime.now()))

        # prepare API endpoint request
        endpoint = "%s/live/quickstats/v3/?apikey=%s&host=" \
            % (options.chartbeat_url, options.API)
        sites_urls = [''.join([endpoint, site]) for site in options.sites]
        responses = None
        try:
            # request chartbeat data from all seven sites at once ...
            # it's so magical!
            responses = yield [http_client.fetch(site) for site in sites_urls]
            visits = 0
            recirculation = 0
            article = 0
            for response in responses:
                body = json.loads(response.body.decode('utf-8'))
                visits += body['visits']
                recirculation += body['recirc']
                article += body['article']
        except Exception as e:
            logging.exception(e)
            logging.info("HTTP Reqs failed")
        logging.info("After quickstats try except")

        # Possibly hacky?  Beat modules are in a list and iterated over
        for beat in BEATS:
            name = beat.__name__
            users = len(beat.connections)
            if beat.connections:
                beat.init(http_client, responses)
                logging.info("{} finished init for ({}) users".format(name, users))
                if name == "beats.viewers":
                    for conn in viewers.connections:
                        conn.write_message({
                            "visits": visits
                        })
                elif name == "beats.popular":
                    for conn in popular.connections:
                        conn.write_message({
                            "users": users,
                            "visits": visits,
                            "recirculation": recirculation,
                            "article": article,
                        })
        logging.info("Heartbeat completed")

        # wait certain time interval before starting process again
        yield gen.Task(loop.add_timeout, timedelta(seconds=7))

def init_server():
    parse_command_line()
    app = Application([
            (r"/", Popular),
            (r"/index", Main),
            (r"/geopoint", GeoPoint),
            (r"/geopoint-socket", geo_point.Socket),
            (r"/engage", Engage),
            (r"/engagesocket", engage.Socket),
            (r"/popular", Popular),
            (r"/popular-socket", popular.Socket),
            (r"/active", Active),
            (r"/active-socket", active.Socket),
            (r"/viewers", Viewers),
            (r"/viewers-socket", viewers.Socket),
            (r"/recirculation", Recirculation),
            (r"/authors", Authors),
            (r"/authors-socket", authors.Socket),
            (r"/stats", Stats),
            (r"/stats-socket", stats.Socket),
            (r"/referral", Referral),
            (r"/referral-socket", referral.Socket),
            (r'/tigers-xtra', TigersXtra)
        ],
        debug=options.debug,
        template_path=os.path.join(base_dir, "templates"),
        static_path=os.path.join(base_dir, "static"),
    )
    app.listen(options.port)
    chartbeat_heartbeat()
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    connections = []
    logging.info("Starting server ...")
    init_server()
