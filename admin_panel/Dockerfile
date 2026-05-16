FROM node:20-alpine

WORKDIR /app

COPY admin_panel/package*.json ./
RUN npm install

COPY admin_panel/ .

EXPOSE 8080

CMD ["npm", "run", "dev"]