FROM mongo:4.4

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.8 python3-pip

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY Pipfile Pipfile.lock /app/
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install pipenv && pipenv install --system

# copy the project code
COPY src /app/src
COPY run.py /app/

# expose the port
EXPOSE 7507

ENV FLASK_ENV production
ENV MONGO_URI mongodb://localhost:27017/db

# define the default command to run when starting the container
CMD ["gunicorn", "--bind", ":7507", "--log-level=info", "--access-logfile", "-", "run:app"]
