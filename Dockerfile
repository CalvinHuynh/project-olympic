FROM python:alpine

RUN mkdir -p /app
WORKDIR /app
ENV FLASK_APP test.py
# ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "flask", "run" ]
