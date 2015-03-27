FROM dockerfile/nodejs-bower-grunt
MAINTAINER Eric Bower neurosnap@gmail.com

RUN git config --global url."https://".insteadOf git://

EXPOSE 80
EXPOSE 8000

WORKDIR /srv/

# install python dependencies
ADD ./conf/requirements.txt /srv/requirements.txt
RUN pip install -r requirements.txt

CMD ["/usr/bin/python", "run.py"]
