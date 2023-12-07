#FROM andrejreznik/python-gdal:py3.10.0-gdal3.2.3
FROM aleontiev/agrocode_api:ver_pandas_1

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8089

CMD ["python", "manage.py", "run-server"]
