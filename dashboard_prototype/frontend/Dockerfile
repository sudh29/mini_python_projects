# ═══════════════════════════════════════════════════════════════
# Frontend — React + Vite
# ═══════════════════════════════════════════════════════════════

# --- Stage 1: Build ---
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# --- Stage 2: Serve ---
FROM nginx:alpine

# Copy build artifacts from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Default command starts nginx
CMD ["nginx", "-g", "daemon off;"]
