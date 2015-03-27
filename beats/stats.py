""" Primary functionality for the stats dashboard """
# Python imports
import json
import logging

# Tornado imports
import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

# Local imports
from lib.util import is_number

connections = []


class Stats:
    __stats = ["social", "links", "search", "direct" ]
    stats = {}

    # Constants
    global TOTAL
    TOTAL = "total"

    def __init__(self):
        for statType in self.__stats:
            self.stats[statType] = {
                TOTAL: 0
                # Will also contain each page's count for that stat
            }
        return

    # Given a response object (via the ChartBeats quickstats api), grab the
    # necessary stats for the site in question
    #
    # @param response - ChartBeats quickstat object
    def addStats(self, site, response):

        # Iterate over the desired stats, and if this stat exists
        # in the response object, add the value
        for statType in self.stats:
            if statType in response:

                # Make sure it's a number
                if is_number(response[statType]):
                    self.stats[statType][TOTAL] += response[statType]
                    self.stats[statType][site] = response[statType]
                #self.stats[statType][statType] = response[statType]
        return ""

    # Return the stats dictionary
    def getStats(self):
        return self.stats


@gen.coroutine
def init(http_client, quickstats):
    logging.info("Stats init()")

    # Save an array of dictionaries that include site and response values
    response_objs = []
    for i in range(0, min(len(quickstats), len(options.sites))):
        response_objs.append({
            "site" : options.sites[i],
            "response" : quickstats[i]
        })

    try:
        # Compile all the pertinent information about each site
        stats = Stats()
        for response in response_objs:
            site = response["site"]
            body = json.loads(response["response"].body.decode('utf-8'))
            stats.addStats(site, body)

        for conn in connections:
            conn.write_message(json.dumps({ "stats" : json.dumps(stats.getStats())}))
    except Exception as e:
        logging.exception(e)


class Socket(tornado.websocket.WebSocketHandler):
    """Stats socket handler"""

    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("Stats page loaded")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("stats.on_message")

    def on_close(self):
        logging.info("Stats page closed")
        connections.remove(self)
