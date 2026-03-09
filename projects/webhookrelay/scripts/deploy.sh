#!/bin/bash
# Deploy WebhookRelay Landing Page to Cloudflare Pages

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC_DIR="$PROJECT_DIR/public"
PROJECT_NAME="webhookrelay"

echo "🚀 Deploying WebhookRelay Landing Page..."
echo "   Project: $PROJECT_NAME"
echo "   Source: $PUBLIC_DIR"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ wrangler not found. Installing..."
    npm install -g wrangler
fi

# Check if user is logged in
echo "📋 Checking Cloudflare authentication..."
if ! wrangler whoami &> /dev/null; then
    echo "⚠️  Not logged in to Cloudflare. Please run: wrangler login"
    exit 1
fi

# Deploy
echo "📦 Deploying to Cloudflare Pages..."
wrangler pages deploy "$PUBLIC_DIR" --project-name="$PROJECT_NAME"

echo "✅ Deployment complete!"
echo "   URL: https://$PROJECT_NAME.pages.dev"