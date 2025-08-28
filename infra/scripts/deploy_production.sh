#!/bin/bash

# Production Deployment Script for Trailium
# This script deploys the application to production with proper checks

set -e  # Exit on any error

# Configuration
PROJECT_NAME="trailium"
DEPLOYMENT_DIR="/opt/trailium"
BACKUP_DIR="/opt/backups"
LOG_FILE="/var/log/trailium/deployment.log"
ENV_FILE=".env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Check if environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    error "Environment file $ENV_FILE not found. Please create it first."
fi

log "Starting production deployment for $PROJECT_NAME"

# Pre-deployment checks
log "Running pre-deployment checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running. Please start Docker first."
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed or not in PATH."
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [[ $DISK_USAGE -gt 90 ]]; then
    error "Disk usage is too high: ${DISK_USAGE}%. Please free up space first."
fi

# Check memory
MEMORY_AVAILABLE=$(free -m | awk 'NR==2{printf "%.0f", $7*100/$2}')
if [[ $MEMORY_AVAILABLE -lt 100 ]]; then
    warning "Available memory is low: ${MEMORY_AVAILABLE}MB"
fi

log "Pre-deployment checks passed"

# Create backup
log "Creating backup of current deployment..."
BACKUP_NAME="${PROJECT_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
if [[ -d "$DEPLOYMENT_DIR" ]]; then
    sudo cp -r "$DEPLOYMENT_DIR" "$BACKUP_DIR/$BACKUP_NAME"
    log "Backup created: $BACKUP_DIR/$BACKUP_NAME"
else
    log "No existing deployment found, skipping backup"
fi

# Stop existing services
log "Stopping existing services..."
cd infra/compose
if docker-compose ps | grep -q "Up"; then
    docker-compose down
    log "Existing services stopped"
else
    log "No running services found"
fi

# Pull latest changes
log "Pulling latest changes..."
git pull origin main

# Build new images
log "Building new Docker images..."
docker-compose build --no-cache

# Validate environment
log "Validating environment configuration..."
if ! docker-compose config > /dev/null; then
    error "Docker Compose configuration is invalid"
fi

# Start services
log "Starting services..."
docker-compose up -d

# Wait for services to be healthy
log "Waiting for services to be healthy..."
TIMEOUT=300
ELAPSED=0
while [[ $ELAPSED -lt $TIMEOUT ]]; do
    if docker-compose ps | grep -q "healthy"; then
        log "Services are healthy"
        break
    fi
    sleep 10
    ELAPSED=$((ELAPSED + 10))
    log "Waiting for services... ($ELAPSED/$TIMEOUT seconds)"
done

if [[ $ELAPSED -ge $TIMEOUT ]]; then
    error "Services failed to become healthy within $TIMEOUT seconds"
fi

# Run health checks
log "Running health checks..."
HEALTH_CHECK_URL="http://localhost/health/"
MAX_RETRIES=5
RETRY_COUNT=0

while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
    if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        log "Health check passed"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    log "Health check failed, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 30
done

if [[ $RETRY_COUNT -ge $MAX_RETRIES ]]; then
    error "Health check failed after $MAX_RETRIES attempts"
fi

# Run database migrations
log "Running database migrations..."
docker-compose exec -T api python manage.py migrate --noinput

# Collect static files
log "Collecting static files..."
docker-compose exec -T api python manage.py collectstatic --noinput

# Clear cache
log "Clearing cache..."
docker-compose exec -T api python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Final health check
log "Running final health check..."
if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
    log "Final health check passed"
else
    error "Final health check failed"
fi

# Show service status
log "Deployment completed successfully!"
log "Service status:"
docker-compose ps

log "Application is available at:"
log "  - Frontend: http://localhost:5173"
log "  - Backend: http://localhost:8000"
log "  - Health: http://localhost/health/"

# Cleanup old backups (keep last 5)
log "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t | tail -n +6 | xargs -r rm -rf

log "Production deployment completed successfully!"
