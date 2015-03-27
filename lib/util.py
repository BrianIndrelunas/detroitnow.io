# Utility functions that might be useful across the site
import re
import random
import math

from tornado.options import options

def is_section_page(url):
    # remove non-articles from popular
    if (url != ""
        and not re.search("story/", url)
        and not re.search("article/", url)
        and not re.search("picture-gallery/", url)
        and not re.search("longform/", url)):
            return True
    return False

# Given any arbitrary value, return True if it's a number, False otherwise
def is_number(value):
	try:
		float(value)
		return True
	except:
		return False

def get_random_site(ignore_site=None):
    """Get a random site using options.sites. Add optional parameter for site
        to ignore_site

        :param ignore_site: Optional string parameter, indicating a site to
                            ignore. Usually used to not get the same random
                            site twice in a row.
                            If None, no site comparison will occur
    """
    num_sites = len(options.sites)
    random_index = random.randint(0, num_sites - 1)
    random_site = options.sites[random_index]

    return random_site

def get_distance(x1, y1, x2, y2):
    """Get the distance between two points http://en.wikipedia.org/wiki/Distance#Geometry

        :param x1: X value of point 1
        :param y1: Y value of point 1
        :param x2: X value of point 2
        :param y2: Y value of point2
    """

    # Get the delta values
    x_delta = abs(x1 - x2)
    y_delta = abs(y1 - y2)

    # Square them
    x_val = x_delta ** 2
    y_val = y_delta ** 2

    final_val = math.sqrt(x_val + y_val)

    return final_val




