FROM python:3.10


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY . /app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver"]

