FROM php:8.2-apache
COPY src/ /var/www/html/
RUN echo "LAB{xxe_lectura_de_archivos_via_entidad_externa}" > /var/www/flag.txt
RUN chmod 644 /var/www/flag.txt
