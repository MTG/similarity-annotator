FROM python:3.4
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends cmake libmad0-dev libsndfile1-dev \
  libgd2-xpm-dev libboost-filesystem-dev libboost-program-options-dev \
  libboost-regex-dev && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/

RUN python manage.py collectstatic --no-input

