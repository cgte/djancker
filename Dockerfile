FROM python:3.7-alpine
COPY . /app
WORKDIR /app


#RUN service nginx start
EXPOSE 8080
CMD ["python","app.py"]

