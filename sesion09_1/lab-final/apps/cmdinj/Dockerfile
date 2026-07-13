FROM php:8.2-apache
COPY src/ /var/www/html/
RUN echo "LAB{command_injection_en_duplicado_de_documentos}" > /var/www/flag.txt
RUN chmod 644 /var/www/flag.txt
