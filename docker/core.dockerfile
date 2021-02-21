FROM python:3.7
ENV PYTHONUNBUFFERED=1
WORKDIR /app2net_core
COPY app2net_core/requirements.txt /app2net_core
RUN pip install -r requirements.txt
COPY app2net_core/* /app2net_core/