FROM python:alpine

RUN mkdir -p /api
WORKDIR /api
ENV FLASK_APP app.py
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "flask", "run" ]
