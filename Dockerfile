FROM debian:buster-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    uwsgi-core \
    uwsgi-plugin-python3 \
    nginx \
    python3-pandas \
    python3-numpy \
    python3-tk \
    ghostscript \
    libcap2-bin \
    libopencv-dev \
    python3-opencv

#RUN useradd www

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt \
    && rm /requirements.txt

COPY nginx.conf /etc/nginx
COPY start.sh /
RUN chmod +x /start.sh

WORKDIR app
COPY src .
RUN mkdir ./tmp && mkdir ./tmp/camelot && mkdir ./tmp/camelot/jsons

RUN touch /run/nginx.pid \
    && chown www-data:www-data -R . /var/log/nginx /var/lib/nginx /run/nginx.pid \
    && setcap CAP_NET_BIND_SERVICE=+eip /usr/sbin/nginx

USER www-data

CMD ["/start.sh"]