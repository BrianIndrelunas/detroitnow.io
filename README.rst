DetroitNow.io
=============

Async, non-blocking HTTP web server and framework,
designed to pull live data from multiple
websites using Chartbeat's API

Requirements
------------

* Python 2.7 -> 3.4
* Node.js (http://www.nodejs.org/)
* Bower (http://bower.io/)
* Tornado (http://www.tornadoweb.org/)

How To -- Manual Mode (Preferred)
---------------------------------

Install Node.js
Install Bower:

.. code:: bash

    npm install -g bower

Pull github repository:

.. code:: bash

    git clone <repo name>

Install javascript dependencies:

.. code:: bash

    bower install

Create virtualenv (optional):

.. code:: bash

    mkvirtualenv detroitnow

Install python dependencies:

.. code:: bash

    pip install -r conf/requirements.txt

Create settings.cfg file if it doesn't exist

.. code:: bash

    debug=True
    port=8000
    API="API KEY HERE"
    sites = (
        "detroitnews.com",
        "freep.com",
    )

Replace all the sites with the sites you have access to

Run the server:

.. code:: bash

    python run.py

Point browser to http://localhost:8000

How To -- Automatic
-------------------

* Install Docker https://docs.docker.com/installation/
* If not on linux distro (i.e. you are running Windows or Mac OSX), then run boot2docker
* When boot2docker boots you should see an IP address, that's the IP you will put into your browser
* If on linux distro then 127.0.0.1, 0.0.0.0, or localhost will be the IP

.. code:: bash

    $ source build.sh

.. code:: bash

    $ source run.sh

Point browser to IP, run.sh runs on port 80 by default

Run Tests
---------

.. code:: bash

    $ pip install nose
    $ nosetests

Credits
-------
* Eric Bower
* Mike Varano
* Reid Williams
