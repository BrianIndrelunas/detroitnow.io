# -*- coding: utf-8 -*-
""" Primary functionality for the authors dashboard """
import json
import logging

import tornado.websocket
from tornado.options import options
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from lib.util import is_section_page

connections = []


class Author(object):
    def __init__(self, name):
        self.name = name
        self.articles = []

    @property
    def total_visits(self):
        visits = 0
        for article in self.articles:
            visits += article.visits
        return visits

    @property
    def json(self):
        return {
            "name": self.name,
            "total_visits": self.total_visits,
            "articles": [article.json for article in self.articles]
        }

    def __repr__(self):
        return "<Author {0}>".format(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class Article(object):
    def __init__(self, title, url, visits, raw_authors):
        self.title = title
        self.url = url
        self.visits = visits
        self.raw_authors = raw_authors

    @property
    def json(self):
        return {
            "title": self.title,
            "url": self.url,
            "visits": self.visits,
            "raw_authors": self.raw_authors
        }

    def __repr__(self):
        return "<Article {0}>".format(self.title)

    def __eq__(self, other):
        return self.url == other.url

@gen.coroutine
def init(http_client, quickstats):
    """ Use toppages to determine author popularity right now """
    logging.info("Authors init()")
    #http_client = AsyncHTTPClient()
    endpoint = "%s/live/toppages/v3/?limit=100&apikey=%s&sort_by=visits&host=" \
        % (options.chartbeat_url, options.API)
    sites = [''.join([endpoint, site]) for site in options.sites]

    try:
        responses = yield [http_client.fetch(site) for site in sites]
    except HTTPError as err:
        logging.info("HTTP Error: %s" % err)
    authors = []
    # loop through all chartbeat sites
    for response in responses:
        body = json.loads(response.body.decode('utf-8'))
        # loop dictionary within pages
        for item in body['pages']:
            try:
                # ensure all keys exist
                keys = ["path", "title", "authors", "stats"]
                key_error = False
                for key in keys:
                    if key not in item:
                        key_error = True
                        break

                # dont bother with objects with missing keys
                if key_error or "visits" not in item['stats']:
                    continue
                # empty titles are useless, why do they exist at all?
                if item["title"] == "" or item["title"] == " ":
                    continue
                # remove non-articles from popular
                if is_section_page(item['path']):
                    continue

                prepd_authors = []
                # pre-processing required to remove erroneous authors
                # or combined authors into a single string
                for auth in item['authors']:
                    auth = auth.replace("by", "")
                    auth = auth.replace("the", "")
                    if auth[:3] == "and":
                        auth = auth[3:]

                    # break up authors who include multiple names
                    if " and " in auth:
                        prepd_authors.extend(auth.split(" and "))
                    else:
                        prepd_authors.append(auth)

                new_article = Article(item['title'], item['path'],
                                      item['stats']['visits'], item['authors'])

                # accumulate all authors into an array of dictionaries
                for auth in prepd_authors:
                    if auth == "" or auth == " ":
                        continue
                    auth = auth.strip()

                    new_author = Author(auth.title())
                    if new_article not in new_author.articles:
                        new_author.articles.append(new_article)

                    found_author = False
                    for author in authors:
                        if author == new_author:
                            if new_article not in author.articles:
                                author.articles.append(new_article)
                            found_author = True
                            break
                    if not found_author:
                        authors.append(new_author)
            except Exception as err:
                print(err)

    authors.sort(key=lambda author: author.total_visits, reverse=True)

    for conn in connections:
        conn.write_message({
            "authors": {
                "name": "authors",
                "children": [author.json for author in authors][:50]
            }
        })


class Socket(tornado.websocket.WebSocketHandler):
    """ Authors dashboard websocket """

    def open(self):
        if self not in connections:
            connections.append(self)
        logging.info("New author connection")
        self.write_message(json.dumps({ "users": len(connections) }))

    def on_message(self, message):
        logging.info("Author on message")

    def on_close(self):
        logging.info("Author connection closed")
        connections.remove(self)
