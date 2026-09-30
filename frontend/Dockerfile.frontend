# ==========================================
# ENTERPRISE FRONTEND BUILDER (Nginx)
# ==========================================
FROM node:18-alpine as builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ENV VITE_API_URL="https://jansetu-backend-297907968720.us-central1.run.app"
ENV VITE_GOOGLE_MAPS_API_KEY="AIzaSyCRB80aqXvG6XIEHstEBTzTJmukGRRxmTs"
RUN npm run build

FROM nginx:alpine
# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
