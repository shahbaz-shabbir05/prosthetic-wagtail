FROM alpine:3.21

RUN apk add lighttpd

CMD ["lighttpd"]