FROM python:3

RUN mkdir /db

WORKDIR /flask_app

COPY . .
RUN pip install -r requirements.txt

CMD ["python", "app.py"]

