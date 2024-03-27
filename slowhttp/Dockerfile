# Use a base image
FROM ubuntu:20.04

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y build-essential git automake autoconf libtool curl && \
    apt-get install -y libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone slowhttptest repository
RUN git clone https://github.com/shekyan/slowhttptest.git /usr/local/src/slowhttptest

# Build slowhttptest
RUN cd /usr/local/src/slowhttptest && \
    autoreconf -fi && \
    ./configure && \
    make && \
    make install

# Clean up
RUN rm -rf /usr/local/src/slowhttptest
