FROM alpine:latest

RUN apk add --no-cache sqlite

WORKDIR /app

COPY init-db.sh /app/

RUN chmod +x /app/init-db.sh

CMD ["/app/init-db.sh"]
