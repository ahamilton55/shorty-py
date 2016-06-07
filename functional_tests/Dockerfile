# Docker container for running headless Firefox Selenium Tests
FROM library/ubuntu:14.04
MAINTAINER Andrew Hamilton <andrew.hamilton@zefr.com>

RUN /usr/bin/apt-get update \
    && /usr/bin/apt-get install -y xvfb firefox python3-pip \
    && /usr/bin/pip3 install selenium pyvirtualdisplay pytest
