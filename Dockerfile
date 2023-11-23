# 1. Base image
FROM python:3.12.0-slim-bookworm
# 2. Copy files
COPY src /src
# 3. Install dependencies
RUN pip3 install -r /src/requirements.txt