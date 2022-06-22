FROM mcr.microsoft.com/playwright/python:v1.22.0-focal

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY lakat ./lakat/
COPY config.yml ./

CMD [ "python", "-m", "lakat" ]
