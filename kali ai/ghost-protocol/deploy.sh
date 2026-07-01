#!/bin/bash
# ⚔️ GHOST PROTOCOL — DEPLOYMENT SCRIPT
# ========================================
# One-command deployment of the complete stack

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║  ⚔️ GHOST PROTOCOL DEPLOYMENT                    ║"
echo "╚══════════════════════════════════════════════════╝"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required. Run setup.sh first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required. Run setup.sh first."; exit 1; }

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found. Create from .env.example"
    echo "   cp .env.example .env"
    exit 1
fi

# Source environment
source .env

# Validate required vars
if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" = "YOUR_TELEGRAM_BOT_TOKEN_HERE" ]; then
    echo "❌ TELEGRAM_TOKEN not set in .env"
    exit 1
fi

echo ""
echo "[*] Building Docker images..."
docker-compose build

echo "[*] Starting containers..."
docker-compose up -d

echo "[*] Waiting for services..."
sleep 10

echo "[*] Verifying services..."
docker-compose ps

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE                          ║"
echo "║                                                  ║"
echo "║  📡 Send /start to your Telegram bot             ║"
echo "║  📊 Status: docker-compose ps                    ║"
echo "║  📋 Logs: docker-compose logs -f                 ║"
echo "╚══════════════════════════════════════════════════╝"