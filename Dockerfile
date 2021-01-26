FROM ubuntu:18.04

WORKDIR /app
RUN apt-get update
RUN apt-get install python3 python3-pip socat nginx -y
RUN python3 -m pip install requests

COPY . /app

EXPOSE 80
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]