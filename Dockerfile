FROM geopython/pygeoapi


WORKDIR /usr/app

COPY ./ ./

RUN python3 read_data.py

ENTRYPOINT ["tail", "-f", "/dev/null"]
