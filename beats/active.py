""" Primary functionality for the active concurrent dashboard """
import json
import logging

import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

connections = []

@gen.coroutine
def init(http_client, quickstats):
    """ The magic of async:  request all data simultaneously in parallel
    and bring all that data into the responses variable while ensuring
    the process is not being blocked waiting for the responses """
    logging.info("Active init()")
    #http_client = AsyncHTTPClient()
    endpoint = "{0}/live/summary/v3/?apikey={1}&keys={2}&host=" \
                .format(options.chartbeat_url, options.API, "read,write,idle")
    active_sites = [''.join([endpoint, site]) for site in options.sites]
    try:
        responses = yield [http_client.fetch(site) for site in active_sites]
        totals = {
            "read": 0,
            "write": 0,
            "idle": 0,
        }
        for response in responses:
            res = json.loads(response.body.decode('utf-8'))
            """data = {
                "read": res['read']['data']['sum'],
                "write": res['write']['data']['sum'],
                "idle": res['idle']['data']['sum'],
            }"""
            totals['read'] += res['read']['data']['sum']
            totals['write'] += res['write']['data']['sum']
            totals['idle'] += res['idle']['data']['sum']
        for conn in connections:
            conn.write_message({
                "users": len(connections),
                "active": totals
            })
    except:
        logging.info("HTTP Reqs failed")

class Socket(tornado.websocket.WebSocketHandler):
    """ Active dashboard websocket """
    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New active connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("Active on message")

    def on_close(self):
        logging.info("Active connection closed")
        connections.remove(self)
