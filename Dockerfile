FROM geopython/pygeoapi


WORKDIR /usr/app

COPY ./ ./

RUN pip3 install -r requirements.txt


ENTRYPOINT ["jupyter"] 
CMD ["notebook", "--ip='*'", "--no-browser"]

