# Docker Basics

Core concepts and workflows for Docker containerization.

## Core Concepts

**Containers:** Lightweight, isolated processes bundling apps with dependencies. Ephemeral by default.

**Images:** Read-only blueprints for containers. Layered filesystem for reusability.

**Volumes:** Persistent storage surviving container deletion.

**Networks:** Enable container communication.

## Dockerfile Best Practices

### Essential Instructions
```dockerfile
FROM node:20-alpine              # Base image (use specific versions)
WORKDIR /app                     # Working directory
COPY package*.json ./            # Copy dependency files first
RUN npm install --production     # Execute build commands
COPY . .                         # Copy application code
ENV NODE_ENV=production          # Environment variables
EXPOSE 3000                      # Document exposed ports
USER node                        # Run as non-root (security)
CMD ["node", "server.js"]        # Default command
```

### Multi-Stage Builds (Production)
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

Benefits: Smaller images, improved security, no build tools in production.

### .dockerignore
```
node_modules
.git
.env
*.log
.DS_Store
README.md
docker-compose.yml
dist
coverage
```

## Building Images

```bash
# Build with tag
docker build -t myapp:1.0 .

# Build targeting specific stage
docker build -t myapp:dev --target build .

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:1.0 .

# View layers
docker image history myapp:1.0
```

## Running Containers

```bash
# Basic run
docker run myapp:1.0

# Background (detached)
docker run -d --name myapp myapp:1.0

# Port mapping (host:container)
docker run -p 8080:3000 myapp:1.0

# Environment variables
docker run -e NODE_ENV=production myapp:1.0

# Volume mount (named volume)
docker run -v mydata:/app/data myapp:1.0

# Bind mount (development)
docker run -v $(pwd)/src:/app/src myapp:1.0

# Resource limits
docker run --memory 512m --cpus 0.5 myapp:1.0

# Interactive terminal
docker run -it myapp:1.0 /bin/sh
```

## Container Management

```bash
# List containers
docker ps
docker ps -a

# Logs
docker logs myapp
docker logs -f myapp          # Follow
docker logs --tail 100 myapp  # Last 100 lines

# Execute command
docker exec myapp ls /app
docker exec -it myapp /bin/sh  # Interactive shell

# Stop/start
docker stop myapp
docker start myapp

# Remove
docker rm myapp
docker rm -f myapp  # Force remove running

# Inspect
docker inspect myapp

# Monitor resources
docker stats myapp

# Copy files
docker cp myapp:/app/logs ./logs
```

## Volume Management

```bash
# Create volume
docker volume create mydata

# List volumes
