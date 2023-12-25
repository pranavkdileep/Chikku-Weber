FROM python:latest

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
RUN mkdir -p uploads && chmod 777 uploads

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--timeout", "300", "main:app"]
