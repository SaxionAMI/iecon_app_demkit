FROM python:3.7.16-slim
COPY requirements.txt /
#RUN apk-get update && apk-get add python3-dev gcc libc-dev
RUN pip3 install -r /requirements.txt
WORKDIR /app
ENTRYPOINT ["python",  "-u" , "/app/demkit.py", "-f", "example", "-m", "demohouse"]