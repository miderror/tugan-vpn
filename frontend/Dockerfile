FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm install

# ================= DEVELOPMENT =================
FROM base AS dev
CMD ["npm", "run", "dev", "--", "--host"]

# ================= PRODUCTION BUILD =================
FROM base AS build
COPY . .
RUN npx vite build

FROM alpine:3.19 AS prod-exporter
WORKDIR /app
COPY --from=build /app/dist ./dist
CMD ["cp", "-r", "dist/.", "/frontend_static/"]
