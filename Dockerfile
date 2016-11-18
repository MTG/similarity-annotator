FROM python:3.4
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends cmake libmad0-dev libsndfile1-dev \
  libgd2-xpm-dev libboost-filesystem-dev libboost-program-options-dev \
  libboost-regex-dev && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

RUN wget -O audiowaveform.tar.gz https://github.com/bbc/audiowaveform/archive/1.0.11.tar.gz && tar xfz audiowaveform.tar.gz \
 && cd audiowaveform-1.0.11 && cmake -DENABLE_TESTS=0 . && make && make install && cd .. && rm -r audiowaveform*

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD package.json /code/
RUN npm install

# Copy installed node packages to /static
RUN mkdir -p /static
ADD Makefile /code/
RUN make

ADD . /code/

RUN python manage.py collectstatic --no-input

