FROM python:3.12-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps

COPY lakat ./lakat/
COPY config.yml ./

CMD [ "python", "-m", "lakat" ]
