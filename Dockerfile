FROM alpine:latest

RUN apk add --no-cache \
    nmap \
    nmap-scripts \
    nmap-nselibs \
    python3 \
    py3-pip \
    coreutils \
    msmtp \
    ca-certificates \
    openssh-client \
    sshpass \
    iproute2 \
    tzdata

# 2. Configure Time Zone
ENV TZ=Europe/Warsaw
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install python-nmap
RUN pip3 install --break-system-packages python-nmap requests

# Email configuration
COPY msmtprc.tpl /etc/msmtprc
RUN chmod 600 /etc/msmtprc

# Scripts
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Optional: Python modules folder
COPY scanner /scanner

VOLUME ["/data"]
VOLUME ["/summary"]

ENTRYPOINT ["/start.sh"]