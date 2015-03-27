""" Primary functionality for the toppage dashboard """
import re
import six
import json
import urllib
import logging
from datetime import date, timedelta

import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

connections = []
http_client = AsyncHTTPClient()

@gen.coroutine
def init(http_client, quickstats):
    """ Get all the data needed for total viewers in a time series
    for today (default) """
    logging.info("Viewers init()")
    #http_client = AsyncHTTPClient()
    endpoint = "%s/historical/traffic/series/?apikey=%s&host=" \
        % (options.chartbeat_url, options.API)
    sites = [''.join([endpoint, site]) for site in options.sites]
    try:
        responses = yield [http_client.fetch(site) for site in sites]
    except HTTPError as err:
        logging.info("HTTP Error: %s" % err)

    viewers_today = None
    for response in responses:
        body = json.loads(response.body.decode('utf-8'))
        start = body['data']['start']
        end = body['data']['end']
        frequency = body['data']['frequency']
        for key, value in six.iteritems(body['data']):
            if key in options.sites:
                if viewers_today is None:
                    viewers_today = value['series']['people']
                else:
                    # sum each element in sequence between two lists into one list
                    # fuckin love python
                    arr = []
                    for x, y in zip(viewers_today, value['series']['people']):
                        if x is not None and y is not None:
                            arr.append(x + y)
                        #else:
                        #    arr.append(0)
                    viewers_today = arr
                break

    for conn in connections:
        conn.write_message({
            "viewers_today": {
                "series": viewers_today,
                "start": start,
                "end": end,
                "frequency": frequency
            }
        })


class Socket(tornado.websocket.WebSocketHandler):
    """ Viewers dashboard websocket """
    @gen.coroutine
    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New viewers connection")

        yesterday = date.today() - timedelta(days=1)
        yesterday.strftime('%Y-%m-%d')

        endpoint = "{0}/historical/traffic/series/?start={1}%2000:00:00&end={1}%2023:59:59&apikey={2}&host=" \
                    .format(options.chartbeat_url, yesterday, options.API)

        sites = [''.join([endpoint, site]) for site in options.sites]

        viewers_yday = None

        try:
            responses = yield [http_client.fetch(site) for site in sites]
        except HTTPError as err:
            logging.info("HTTP Error: %s" % err)

        for response in responses:
            body = json.loads(response.body.decode('utf-8'))
            start = body['data']['start']
            end = body['data']['end']
            frequency = body['data']['frequency']

            for key, value in six.iteritems(body['data']):
                if key in options.sites:
                    if viewers_yday is None:
                        viewers_yday = value['series']['people']
                    else:
                        # sum each element in sequence between two lists into one list
                        # fuckin love python
                        arr = []
                        for x, y in zip(viewers_yday, value['series']['people']):
                            if x is not None and y is not None:
                                arr.append(x + y)
                        viewers_yday = arr
                    break

        data = json.dumps({
                "users": len(connections),
                "viewers_yday": {
                    "series": viewers_yday,
                    "start": start,
                    "end": end,
                    "frequency": frequency
                }})
        self.write_message(data)

    def on_message(self, message):
        logging.info("On message")

    def on_close(self):
        logging.info("Viewers connection closed")
        connections.remove(self)
