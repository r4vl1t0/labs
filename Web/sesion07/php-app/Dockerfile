FROM php:8.2-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends libxml2-dev pkg-config \
    && docker-php-ext-install dom \
    && rm -rf /var/lib/apt/lists/*
RUN a2enmod rewrite \
    && sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf \
    && printf 'ErrorDocument 404 /index.php\n' > /etc/apache2/conf-available/lab-routes.conf \
    && a2enconf lab-routes

COPY index.php /var/www/html/index.php
COPY .htaccess /var/www/html/.htaccess
RUN mkdir -p /flags \
    && printf 'FLAG{A_XXE_BASE64_INDEX_DISCLOSURE}\n' > /flags/A_xxe.txt \
    && printf 'FLAG{B_XXE_REPORT_USER_FILE_READ}\n' > /flags/B_xxe.txt \
    && printf 'FLAG{FINAL_IDOR_PROJECT_ONE}\n' > /flags/final_idor.txt \
    && printf 'FLAG{FINAL_XXE_REPORT_CREATOR}\n' > /flags/final_xxe.txt \
    && printf 'Panel interno Zorum\nClave de reporte: FLAG{FINAL_XXE_REPORT_CREATOR}\n' > /var/www/html/final_secret.txt \
    && chown -R www-data:www-data /var/www/html

EXPOSE 80
