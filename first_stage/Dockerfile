FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y apache2 libapache2-mod-security2 && \
    apt-get install -y openssl && \
    apt-get install -y dos2unix && \
    apt-get clean

# Set up working directory
WORKDIR /app

# Copy application files
COPY app.py /app
COPY requirements.txt /app
COPY check_signatures.py /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN dos2unix check_signatures.py
RUN chmod 777 check_signatures.py
RUN chmod 755 /app

# Set up Apache and ModSecurity
RUN a2enmod security2 proxy proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html

# Copy ModSecurity configuration files
COPY mod_security.conf /etc/modsecurity/modsecurity.conf
COPY custom_rules.conf /etc/modsecurity/custom_rules.conf

# Configure Apache to proxy requests to the Flask app
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && \
    echo "ProxyPass / http://127.0.0.1:88/" >> /etc/apache2/sites-available/000-default.conf && \
    echo "ProxyPassReverse / http://127.0.0.1:88/" >> /etc/apache2/sites-available/000-default.conf

# Expose port 80
EXPOSE 80

# Start Apache and Flask app
CMD ["sh","-c","service apache2 start && python /app/app.py"]
