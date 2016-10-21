FROM ubuntu:14.04

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y openssl python-imaging python-jinja2 python-lxml libxml2-dev libxslt1-dev python-pgpdump spambayes

WORKDIR /Mailpile

# Create users and groups
RUN groupadd -r mailpile \
    && mkdir -p /mailpile-data/.gnupg \
    && useradd -r -d /mailpile-data -g mailpile mailpile

# Add GnuPG placeholder file
RUN touch /mailpile-data/.gnupg/docker_placeholder

# Fix permissions
RUN chown -R mailpile:mailpile /Mailpile
RUN chown -R mailpile:mailpile /mailpile-data

# Run as non-privileged user
USER mailpile

EXPOSE 33411
