FROM golang:1.13.5-alpine3.11 AS builder

LABEL maintainer="Phil Pennock <noc+openpgpkey@pennock-tech.com>"

WORKDIR /tmp/build

COPY . /tmp/openpgpkey/

RUN apk add --update git

RUN git clone https://github.com/mholt/caddy && cd caddy \
	&& sed -i~ -e 's/EnableTelemetry = true/EnableTelemetry = false/' caddy/caddymain/run.go \
	&& CGO_ENABLED=0 go install -ldflags -s ./caddy/...

FROM alpine:3.11

COPY --from=builder /go/bin/caddy /bin/
COPY --from=builder /tmp/openpgpkey/ /srv/repo

VOLUME /root/.caddy

WORKDIR /srv/repo
CMD ["caddy"]

EXPOSE 80
EXPOSE 443
