FROM python:3.12-slim

WORKDIR /app

COPY app.py /app/app.py
COPY uploads /app/uploads

RUN printf '%s\n' 'FLAG{FINAL_LFI_APIV1_BYPASS_2026}' > /flag.txt \
    && printf '%s\n' 'FLAG{ALUMNO_LFI_NORMAL_2026}' > /flag_lab3_alumno.txt \
    && printf '%s\n' 'FLAG{PROFESOR_LFI_NORMAL_2026}' > /flag_lab3_profesor.txt

EXPOSE 8000

CMD ["python", "app.py"]
