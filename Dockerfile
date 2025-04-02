FROM node:18-alpine

RUN npm install -g json-server

WORKDIR /app

COPY db.json /app/db.json

EXPOSE 3000

CMD ["json-server", "--watch", "db.json", "--port", "3000"]
