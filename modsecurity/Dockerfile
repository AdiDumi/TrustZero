# Install Modsecurity in a Docker container;
FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive
# update/upgrade your system
RUN apt-get update -y

# Install Required Dependencies
RUN apt-get install -y g++ flex bison curl apache2-dev \
	doxygen libyajl-dev ssdeep liblua5.2-dev \
	libgeoip-dev libtool dh-autoreconf \
	libcurl4-gnutls-dev libxml2 libpcre++-dev \
	libxml2-dev git wget tar apache2

# Download LibModsecurity
RUN wget https://github.com/SpiderLabs/ModSecurity/releases/download/v3.0.4/modsecurity-v3.0.4.tar.gz

# Extract the Downloaded File
RUN tar xzf modsecurity-v3.0.4.tar.gz && rm -rf modsecurity-v3.0.4.tar.gz

# Compile and Install LibModsecurity
RUN cd modsecurity-v3.0.4 && \
	./build.sh && ./configure && \
	make && make install

# Install ModSecurity-Apache Connector
RUN cd ~ && git clone https://github.com/SpiderLabs/ModSecurity-apache

RUN cd ~/ModSecurity-apache && \
	./autogen.sh && \
	./configure --with-libmodsecurity=/usr/local/modsecurity/ && \
	make && \
	make install

# Load the Apache ModSecurity Connector Module
RUN echo "LoadModule security3_module /usr/lib/apache2/modules/mod_security3.so" >> /etc/apache2/apache2.conf

# Configure ModSecurity
RUN mkdir /etc/apache2/modsecurity.d && \
	cp modsecurity-v3.0.4/modsecurity.conf-recommended /etc/apache2/modsecurity.d/modsecurity.conf && \
	cp modsecurity-v3.0.4/unicode.mapping /etc/apache2/modsecurity.d/ && \
	sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/apache2/modsecurity.d/modsecurity.conf
ADD modsec_rules.conf /etc/apache2/modsecurity.d/

# Install OWASP ModSecurity Core Rule Set (CRS) on Ubuntu
RUN git clone https://github.com/SpiderLabs/owasp-modsecurity-crs.git /etc/apache2/modsecurity.d/owasp-crs && \
	cp /etc/apache2/modsecurity.d/owasp-crs/crs-setup.conf.example /etc/apache2/modsecurity.d/owasp-crs/crs-setup.conf

# Activate ModSecurity
RUN mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.old
ADD 000-default.conf /etc/apache2/sites-available/

EXPOSE 80
CMD apachectl -D FOREGROUND