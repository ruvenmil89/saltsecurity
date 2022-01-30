FROM python:3.9.10-slim-buster

WORKDIR /opt/saltsecurity

COPY models.json requests.json requestProcessing.py ./

CMD ["python3.9","requestProcessing.py"]