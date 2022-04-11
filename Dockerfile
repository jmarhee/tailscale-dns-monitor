FROM python:3.8

COPY requirements.txt /requirements.txt
COPY tailscale.py /tailscale.py

ENV FORWARDING_NAMESERVERS "8.8.8.8,8.8.4.4"
ENV TAILNET_ID ""
ENV TAILSCALE_TOKEN ""

RUN pip install -r /requirements.txt

ENTRYPOINT python3 /tailscale.py
CMD []
