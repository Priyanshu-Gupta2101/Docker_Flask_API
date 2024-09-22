FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=core/server.py
ENV FLASK_ENV=development
RUN flask db upgrade -d core/migrations/
EXPOSE 8080
CMD ["bash", "run.sh"]