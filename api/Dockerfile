FROM fedora:30

RUN mkdir -p /api
WORKDIR /api
ENV FLASK_APP app.py

RUN dnf install python3 \
        python3-pip \
        chromium \
        firefox \
        -y

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod +x /api/bin/geckodriver && chmod +x /api/bin/chromedriver

CMD [ "flask", "run" ]
