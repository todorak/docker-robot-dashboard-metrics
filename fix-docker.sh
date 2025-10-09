#!/bin/bash
echo "🔧 Fixing Docker cache issue..."

# Stop everything
docker-compose down

# Remove metrics container and image
docker rm -f sunday_metrics 2>/dev/null || true
docker rmi sunday_metrics:latest 2>/dev/null || true

# Start fresh
docker-compose up -d metrics

echo "✅ Done! Check status:"
docker-compose ps metrics
