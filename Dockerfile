# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/dashboard/package*.json ./frontend/dashboard/
RUN cd frontend/dashboard && npm install
COPY frontend/dashboard/ ./frontend/dashboard/
RUN cd frontend/dashboard && npm run build || { echo "Frontend build failed"; exit 1; }

# Stage 2: Build the Node.js backend
FROM node:18-alpine AS backend-builder
WORKDIR /app
COPY backend/package*.json ./backend/
RUN cd backend && npm install
COPY backend/ ./backend/

# Stage 3: Final image (Python + Node + frontend)
FROM python:3.9-slim

# Install system dependencies (for Chromium + Node.js)
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    wget \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

# Copy backend Python scripts + data
COPY backend/scripts/ /app/backend/scripts
COPY backend/data/ /app/backend/data

# Copy Node.js backend
COPY --from=backend-builder /app/backend /app/backend

# Copy React build
COPY --from=frontend-builder /app/frontend/dashboard/dist ./frontend/dashboard/dist

# Copy entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 3000 3001
ENV NODE_ENV=production

CMD ["./entrypoint.sh"]
