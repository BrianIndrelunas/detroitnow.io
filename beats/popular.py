""" Primary functionality for the toppage dashboard """
import re
import json
import logging
import datetime

import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from lib.util import is_section_page

connections = []

@gen.coroutine
def init(http_client, quickstats):
    """ Get all the data needed for the most popular articles """
    logging.info("Popular init()")
    #http_client = AsyncHTTPClient()
    endpoint = "%s/live/toppages/v3/?limit=50&apikey=%s&host=" \
        % (options.chartbeat_url, options.API)
    engage_sites = [''.join([endpoint, site]) for site in options.sites]
    try:
        responses = yield [http_client.fetch(site) for site in engage_sites]
    except HTTPError as err:
        logging.info("HTTP Error: %s" % err)
    data = []
    for response in responses:
        body = json.loads(response.body.decode('utf-8'))
        for item in body['pages']:

            # remove non-articles from popular
            if is_section_page(item['path']):
                continue

            try:
                article = {
                    "path": item['path'],
                    "title": item['title'],
                    "visits": item['stats']['visits'],
                }
            except KeyError as err:
                logging.info("KeyError: %s" % err)
            data.append(article)
    data = sorted(data, key=lambda page: page['visits'], reverse=True)

    for conn in connections:
        conn.write_message({ "popular": data[:40] })


class Socket(tornado.websocket.WebSocketHandler):
    """ Popular dashboard websocket """

    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New popular connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("Popular on message")

    def on_close(self):
        logging.info("Popular connection closed")
        connections.remove(self)
