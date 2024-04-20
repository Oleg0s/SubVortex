FROM python:3.10

WORKDIR /usr/src/app

COPY . .

RUN pip3 install --upgrade requests
# COPY requirements.txt ./
RUN pip3 install -r requirements.txt
# RUN pip3 install flask gunicorn
RUN pip3 install -e .

