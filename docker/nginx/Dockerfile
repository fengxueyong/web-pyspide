# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY ui/package.json ui/package-lock.json* ./
RUN npm ci
COPY ui/index.html ui/vite.config.js ./
COPY ui/src/ ./src/
RUN npm run build

# Nginx stage
FROM nginx:alpine
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
