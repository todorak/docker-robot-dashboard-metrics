FROM python:3.11-slim
LABEL version="latest" maintainer="Sunday Natural Products GmbH"

ARG UID=1000
ARG GID=1000

# Copy requirements
COPY ./robot/requirements.txt /tmp/requirements.txt

# Install system packages and Chrome
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        wget \
        sudo \
        procps && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl-ssl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Install Chrome and Java
RUN apt-get update -y && apt-get install -y --no-install-recommends \
        google-chrome-stable \
        default-jre && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/tmp/*

# Install Python packages
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/*

# Create user
RUN groupadd headless -g $GID && \
    useradd headless --shell /bin/bash --create-home -u $UID -g $GID && \
    usermod -a -G sudo headless && \
    echo 'headless ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Create directories
RUN mkdir -p /robot_src \
             /robot_results \
             /robot_logs && \
    chown -R headless:headless /robot_src \
                               /robot_results \
                               /robot_logs

# Copy scripts
COPY --chown=headless:headless ./robot/entrypoint.sh /entrypoint.sh
COPY --chown=headless:headless ./robot/test_runner.py /test_runner.py
RUN chmod +x /entrypoint.sh

USER headless
WORKDIR /robot_src

ENTRYPOINT ["/entrypoint.sh"]
CMD ["Smoke"]
EXPOSE 7778
