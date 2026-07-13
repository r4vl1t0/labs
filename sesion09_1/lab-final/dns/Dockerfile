FROM ubuntu:22.04
RUN apt-get update && apt-get install -y bind9 bind9utils dnsutils && rm -rf /var/lib/apt/lists/*
COPY named.conf.options /etc/bind/named.conf.options
COPY named.conf.local /etc/bind/named.conf.local
COPY zones/db.lab.local /etc/bind/db.lab.local
RUN chown bind:bind /etc/bind/db.lab.local && chmod 644 /etc/bind/db.lab.local
EXPOSE 53/udp 53/tcp
CMD ["named", "-g", "-c", "/etc/bind/named.conf"]
