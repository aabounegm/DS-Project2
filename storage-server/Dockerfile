FROM python:3.8

RUN mkdir -p /app
WORKDIR /app

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY Pipfile Pipfile.lock /app/
RUN pip install --upgrade pip
RUN pip install pipenv && pipenv install --system

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy the project code
COPY src /app/src
COPY run.py /app/

# expose the port
EXPOSE 7508

ENV FLASK_ENV production

# define the default command to run when starting the container
ENTRYPOINT ["python3.8", "run.py"]
