import os.path
import unittest
import json
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase
from tornado.options import define, options, parse_command_line, \
                                parse_config_file

define("API", default="317a25eccba186e0f6b558f45214c0e7",
        help="chartbeat api key", type=str)
define("chartbeat_url", default="http://api.chartbeat.com",
        help="chartbeat base URL", type=str)
define("sites", default=("avc.com"), help="chartbeat sites", type=tuple)

base_dir = os.path.dirname(os.path.dirname(__file__))
parse_config_file(os.path.join(base_dir, "settings.cfg"))

class TestGeo(unittest.TestCase):
    """ A collection of Geo tests """

    def test_cluster(self):
        """ Test grouping of latitude and longitudes
        that are on top of each other """
        pass

class TestFetch(AsyncTestCase):
    """ Ensure async fetch consistency """

    def setUp(self):
        self.io_loop = self.get_new_ioloop()

    def test_fetch_geo(self):
        """ Ensure ChartBeat request geo data has expected response  """
        client = AsyncHTTPClient(self.io_loop)
        endpoint = "%s/live/geo/v3/?limit=1000&apikey=%s&host=" \
                    % (options.chartbeat_url, options.API)
        geo_sites = [''.join([endpoint, site]) for site in options.sites]
        for site in geo_sites:
            client.fetch(site, self.stop)
        response = self.wait()
        res = json.loads(response.body.decode('utf-8'))
        self.assertIn("lat_lngs", res)
        for coord in res['lat_lngs']:
            self.assertEqual(len(coord), 3)

    def test_fetch_toppage(self):
        """ Ensure ChartBeat request toppage data has expected response """
        client = AsyncHTTPClient(self.io_loop)
        endpoint = "%s/live/quickstats/v3/?apikey=%s&host=" \
                % (options.chartbeat_url, options.API)
        sites_urls = [''.join([endpoint, site]) for site in options.sites]
        for site in sites_urls:
            client.fetch(site, self.stop)
        response = self.wait()
        res = json.loads(response.body.decode('utf-8'))
        self.assertIn("engaged_time", res)
        self.assertIn("avg", res['engaged_time'])

    def test_fetch_engage(self):
        """ Ensure ChartBeat request engaged data has expected response """
        client = AsyncHTTPClient(self.io_loop)
        endpoint = "%s/live/quickstats/v3/?apikey=%s&host=" \
                % (options.chartbeat_url, options.API)
        sites_urls = [''.join([endpoint, site]) for site in options.sites]
        for site in sites_urls:
            client.fetch(site, self.stop)
        response = self.wait()
        res = json.loads(response.body.decode('utf-8'))
        self.assertIn("toppages", res)
        for page in res['toppages']:
            self.assertIn("path", page)
            self.assertIn("visitors", page)

if __name__ == '__main__':
    unittest.main()
