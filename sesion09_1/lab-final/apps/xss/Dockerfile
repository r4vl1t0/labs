FROM php:8.2-apache
RUN docker-php-ext-install mysqli
COPY src/ /var/www/html/
RUN mkdir -p /var/www/html/logs && chown -R www-data:www-data /var/www/html/logs
