""" Primary functionality for the referral concurrent dashboard """
import six
import json
import logging

import tldextract

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
    logging.info("Referral init()")
    #http_client = AsyncHTTPClient()
    endpoint = "{0}/live/referrers/v3/?&limit=100&apikey={1}&host=" \
                .format(options.chartbeat_url, options.API)
    sites = [''.join([endpoint, site]) for site in options.sites]
    try:
        responses = yield [http_client.fetch(site) for site in sites]
        referrals = {}
        for response in responses:
            res = json.loads(response.body.decode('utf-8'))
            for key, value in six.iteritems(res['referrers']):
                # grab domain from referrer
                tld = tldextract.extract(key)
                domain = tld.domain
                # google goggles are everywhere
                if domain == "google":
                    domain = "google search"

                # some parsing and cleaning up of referrers
                if key == "t.co":
                    key = "twitter"
                elif key == "":
                    key = "dark social"
                elif key == "news.google.com":
                    key = "google news"
                elif key == "google.com":
                    key = "google search"
                elif key == "r.search.yahoo.com":
                    key = "yahoo search"
                elif key == "tpc.googlesyndication.com":
                    key = "google adsense"
                elif key == "hsrd.yahoo.com":
                    key = "yahoo news"
                else:
                    key = domain
                # apply title case to keys
                key = key.title()
                if key in referrals:
                    referrals[key] += int(value)
                else:
                    referrals[key] = int(value)
        for conn in connections:
            conn.write_message({
                "users": len(connections),
                "referral": referrals
            })
    except Exception as e:
        logging.warning(e)
        logging.info("HTTP Reqs failed")

class Socket(tornado.websocket.WebSocketHandler):
    """ Referral dashboard websocket """
    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New referral connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("Referral on message")

    def on_close(self):
        logging.info("Referral connection closed")
        connections.remove(self)
