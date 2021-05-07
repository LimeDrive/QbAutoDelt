FROM python:3.9-slim-buster

WORKDIR /qb-auto-delt
ENV TZ=Europe/Paris

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools && pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]