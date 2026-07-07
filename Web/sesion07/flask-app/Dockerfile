FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping coreutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
RUN mkdir -p /app/workspace /flags \
    && printf 'Inventario trimestral\nPendiente de revision\n' > /app/workspace/reporte.txt \
    && printf 'FLAG{A_CMD_INJECTION_1_PANEL_PING}\n' > /flags/A_lab1.txt \
    && printf 'FLAG{B_CMD_INJECTION_1_PIPE_PANEL}\n' > /flags/B_lab1.txt \
    && printf 'FLAG{A_CMD_INJECTION_2_IFS_BYPASS}\n' > /flags/A_lab2.txt \
    && printf 'FLAG{B_CMD_INJECTION_2_WHOAMI_BYPASS}\n' > /flags/B_lab2.txt \
    && printf 'FLAG{A_JINJA2_TEMPLATE_FILE_READ}\n' > /flag.txt \
    && printf 'FLAG{B_JINJA2_RCE_FLAG_2026}\n' > /flag_2026.txt

EXPOSE 5000
CMD ["python", "app.py"]
