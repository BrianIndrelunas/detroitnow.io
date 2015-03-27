""" Primary functionality for the engagement dashboard """
import json
import logging

import tornado.websocket
from tornado.options import options
from tornado import gen

connections = []

@gen.coroutine
def init(http_client, quickstats):
    logging.info("Engage init()")
    data = {}
    for response in quickstats:
        if response.error:
            logging.info("Error: ", response.error)
        else:
            url = response.effective_url
            host = url[url.index("host=")+5:]
            body = json.loads(response.body.decode('utf-8'))
            data[host] = body['engaged_time']
    for conn in connections:
        conn.write_message({ "users": len(connections), "engage": data })


class Socket(tornado.websocket.WebSocketHandler):
    """ Engagement dashboard websocket """

    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New engage connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("Engage on message")

    def on_close(self):
        logging.info("Engage connection closed")
        connections.remove(self)
