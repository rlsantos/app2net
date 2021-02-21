FROM python:latest
COPY ./static_repo /repo/
WORKDIR /repo/
CMD python3 -m http.server 3333
