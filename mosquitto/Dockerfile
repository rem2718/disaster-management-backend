FROM eclipse-mosquitto:latest

RUN apk add --no-cache jq

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY acl.conf /mosquitto/config/acl.conf
COPY passwd /mosquitto/config/passwd
COPY mosquitto_admin.sh /usr/local/bin/mosquitto_admin.sh

RUN chmod +x /usr/local/bin/mosquitto_admin.sh
RUN mosquitto_passwd -b /mosquitto/config/passwd admin-broker AdmBro@1984 && \
    mosquitto_passwd -b /mosquitto/config/passwd admin-web AdmWeb@1984

EXPOSE 1883

CMD ["sh", "-c", "/usr/local/bin/mosquitto_admin.sh"]
