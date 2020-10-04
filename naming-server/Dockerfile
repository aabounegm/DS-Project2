FROM python:latest

RUN mkdir -p /app
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY Pipfile Pipfile.lock /app/
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system

# copy the project code
COPY src /app/src
COPY run.py /app/

# expose the port
EXPOSE 7507

ENV FLASK_ENV production

# define the default command to run when starting the container
CMD ["gunicorn", "--bind", ":7507", "--log-level=info", "--access-logfile", "-", "run:app"]
