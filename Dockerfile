FROM node:18-alpine

RUN npm install -g json-server

WORKDIR /app

COPY db.json /app/db.json

EXPOSE 3000

CMD ["sh", "-c", "cp db.json /tmp/db.json && json-server --watch /tmp/db.json --host 0.0.0.0 --port 3000"]
