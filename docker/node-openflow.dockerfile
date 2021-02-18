FROM linton/docker-ryu
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7 curl
COPY app2net_core/system_notifier/node_communication/env_storage.py /app2net/node_communication/
COPY app2net_core/system_notifier/node_communication/message_server.py /app2net/node_communication/
COPY app2net_core/system_notifier/node_communication/drivers/reference.py /app2net/node_communication/drivers/
COPY app2net_core/system_notifier/node_communication/drivers/openflow_driver.py /app2net/node_communication/drivers/
WORKDIR /app2net/
RUN mkdir node_communication/drivers/logs/
CMD python3.7 -m node_communication.drivers.openflow_driver
