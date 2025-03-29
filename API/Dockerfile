FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# install yandex cloud cli
RUN curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | sudo bash -s -- -i /usr/local/bin

COPY . .
