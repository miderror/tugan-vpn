FROM ghcr.io/mhsanaei/3x-ui:v2.8.11

RUN apk add --no-cache sqlite bash

COPY init.sh /init.sh
RUN chmod +x /init.sh

ENTRYPOINT ["/init.sh"]