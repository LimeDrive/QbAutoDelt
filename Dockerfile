FROM python:3.9-slim-buster

WORKDIR /qb-auto-delt

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV VERIFY_WEBUI_CERTIFICATE=False

CMD ["python3", "main.py"]
