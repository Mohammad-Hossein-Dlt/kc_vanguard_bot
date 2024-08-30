FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get -y update
RUN apt-get -y upgrade

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 80

EXPOSE 8000

CMD ["python", "run.py"]
