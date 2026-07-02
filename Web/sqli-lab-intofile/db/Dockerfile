FROM mysql:5.7

# ADVERTENCIA: esto es INTENCIONALMENTE inseguro, solo para el laboratorio.
COPY secure-file-priv.cnf /etc/mysql/conf.d/secure-file-priv.cnf
COPY init.sql /docker-entrypoint-initdb.d/init.sql
