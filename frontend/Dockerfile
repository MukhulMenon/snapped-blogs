FROM node:16-alpine

ADD . /app/frontend

WORKDIR /app/frontend

RUN npm install

ENTRYPOINT [ "npm" ]

CMD [ "start" ]