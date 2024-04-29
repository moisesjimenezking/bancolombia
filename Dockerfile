FROM python:3.9-alpine

ENV DEBIAN_FRONTEND=noninteractive

COPY .env /app/.env
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apk add --no-cache firefox-esr  # Instalar Firefox

# Instalar las dependencias necesarias para WeasyPrint
RUN apk add --no-cache \
    gobject-introspection \
    py3-gobject3 \
    cairo \
    pango \
    gdk-pixbuf
    
WORKDIR /app

COPY app /app

EXPOSE 23301

CMD ["python", "startApp.py"]