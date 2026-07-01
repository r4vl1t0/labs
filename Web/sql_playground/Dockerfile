FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]
