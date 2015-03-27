""" Primary functionality for the geo location dashboard """
import json
import logging
import random

import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from lib.util import is_section_page, get_random_site, get_distance

connections = []

last_lat_lng = {
    "lat": float("-inf"),
    "lng": float("-inf")
}


@gen.coroutine
def init(http_client, quickstats):
    """ The magic of async:  request all data simultaneously in parallel
    and bring all that data into the responses variable while ensuring
    the process is not being blocked waiting for the responses """
    logging.info("GeoPoint init()")
    endpoint = "%s/live/recent/v3/?limit=50&apikey=%s&host=" % (options.chartbeat_url, options.API)

    random_site = get_random_site()

    api_site = endpoint + random_site
    logging.info(api_site)
    geo_data = {}
    responses = []
    try:
        response = yield http_client.fetch(api_site)
    except:
        response = None
        logging.info("HTTP Reqs failed")

    try:
        if response:
            people = json.loads(response.body.decode('utf-8'))
            num_people = len(people)

            # Grab the first valid article (i.e. not a section page)
            # That's [n] latitude/longitude values away from the last loaded
            # article
            count = 0
            while count < num_people: # Ensure this doesn't infinite loop
                count += 1
                random_index = random.randint(0, num_people - 1)
                person = people[random_index]

                if is_section_page(person['path']):
                    continue
                if person['title'] == "" or person['title'] == " ":
                    continue

                data = {
                    "lat": person['lat'],
                    "lng": person['lng'],
                    "platform": person['platform'],
                    "domain": person['domain'],
                    "host": person['host'],
                    "path": person['path'],
                    "title": person['title'],
                    "user_agent": person['user_agent'],
                    "country": person['country'],
                }
                geo_data = data

                latitude_delta = get_distance(
                                    last_lat_lng["lat"],
                                    last_lat_lng["lng"],
                                    person["lat"],
                                    person["lng"])

                logging.info("DELTA: {0}".format(latitude_delta))

                if latitude_delta > 5.0:
                    break

            last_lat_lng["lat"] = geo_data["lat"]
            last_lat_lng["lng"] = geo_data["lng"]

    except Exception as err:
        logging.exception(err)

    for conn in connections:
            conn.write_message({ "users": len(connections), "geo_point": geo_data })


class Socket(tornado.websocket.WebSocketHandler):
    """ Geo Point dashboard websocket """
    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New geopoint connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("GeoPoint on message")

    def on_close(self):
        logging.info("GeoPoint connection closed")
        connections.remove(self)
