# =======================================================
# STAGE 1: Build Vite / React Application
# =======================================================
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

# =======================================================
# STAGE 2: Serve with Nginx Alpine (Minimal & Hardened)
# =======================================================
FROM nginx:alpine AS runner

# Copiar configuración optimizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar artefactos estáticos compilados desde el builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
