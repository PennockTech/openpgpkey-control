ARG GOPROXY=''

FROM golang:1.17.3-alpine3.14 AS builder
ARG GOPROXY

LABEL maintainer="Phil Pennock <noc+openpgpkey@pennock-tech.com>"

WORKDIR /tmp/build

COPY . /tmp/openpgpkey/

RUN apk add --update git

RUN git clone https://github.com/caddyserver/caddy && cd caddy \
	&& CGO_ENABLED=0 go install -ldflags -s ./cmd/caddy/...

FROM alpine:3.14

COPY --from=builder /go/bin/caddy /bin/
COPY --from=builder /tmp/openpgpkey/ /srv/repo

VOLUME /root/.caddy

WORKDIR /srv/repo
CMD ["caddy", "run"]

EXPOSE 80
EXPOSE 443
