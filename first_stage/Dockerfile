FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y apache2 libapache2-mod-security2 && \
    apt-get install -y incron && \
    apt-get clean

# Set up working directory
WORKDIR /app

# Copy application files
COPY app.py /app
COPY requirements.txt /app

COPY process_log.py /usr/local/bin/process_log.py

# Install Python dependencies
RUN pip install -r requirements.txt

RUN chmod +x /usr/local/bin/process_log.py

# Set up Apache and ModSecurity
RUN a2enmod security2 proxy proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html

# Copy ModSecurity configuration files
COPY mod_security.conf /etc/modsecurity/modsecurity.conf
COPY custom_rules.conf /etc/modsecurity/custom_rules.conf

# Configure Apache to proxy requests to the Flask app
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && \
    echo "ProxyPass / http://127.0.0.1:88/" >> /etc/apache2/sites-available/000-default.conf && \
    echo "ProxyPassReverse / http://127.0.0.1:88/" >> /etc/apache2/sites-available/000-default.conf

RUN touch /etc/incron.d/my_incron_jobs
RUN chmod 644 /etc/incron.d/my_incron_jobs
RUN echo "root" >> /etc/incron.allow
RUN echo "/var/log/apache2/modsec_audit.log IN_MODIFY /usr/local/bin/python /usr/local/bin/process_log.py >> /var/log/process_log.log 2>&1" >> /etc/incron.d/my_incron_jobs
# Expose port 80
EXPOSE 80

# Start Apache and Flask app
CMD ["sh", "-c", "service apache2 start && incrond && python /app/app.py"]
