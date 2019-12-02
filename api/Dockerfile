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
RUN cd /api/bin && chmod +x geckodriver && chmod +x chromedriver

CMD [ "flask", "run" ]
