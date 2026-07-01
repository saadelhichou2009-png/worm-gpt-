#!/bin/bash
# ⚔️ GHOST PROTOCOL — BOOT SEQUENCE

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║     ⚔️ GHOST PROTOCOL BOOT SEQUENCE              ║"
echo "╚══════════════════════════════════════════════════╝"

# === STEP 1: Environment ===
echo "[1/6] Checking environment..."
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure."
    exit 1
fi
source .env

# === STEP 2: Network ===
echo "[2/6] Configuring network layer..."
# Enable IP forwarding for proxy chain
sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1 || true
sysctl -w net.ipv6.conf.all.disable_ipv6=1 > /dev/null 2>&1 || true

# === STEP 3: Docker Services ===
echo "[3/6] Starting Docker services..."
docker-compose up -d ollama redis tor-proxy 2>/dev/null || true

# === STEP 4: AI Models ===
echo "[4/6] Loading AI models..."
if command -v ollama &> /dev/null; then
    ollama pull dolphin-llama3:latest 2>/dev/null || echo "⚠️ Ollama not available, skipping"
    ollama pull wizardlm-uncensored:latest 2>/dev/null || true
else
    echo "⚠️ Ollama not installed. Models will be loaded by container."
fi

# === STEP 5: Ghost C2 ===
echo "[5/6] Starting Ghost C2..."
python3 core/ghost_c2.py &
C2_PID=$!
echo "   C2 PID: $C2_PID"

# === STEP 6: Verification ===
echo "[6/6] Verifying services..."
sleep 3

# Check C2
if kill -0 $C2_PID 2>/dev/null; then
    echo "✅ Ghost C2: Running"
else
    echo "❌ Ghost C2: Failed to start"
fi

# Check AI
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ AI Engine: Running"
else
    echo "⚠️ AI Engine: Not responding"
fi

# Check Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis: Running"
else
    echo "⚠️ Redis: Not available"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ GHOST PROTOCOL ACTIVE                        ║"
echo "║                                                  ║"
echo "║  📡 Send /start to your Telegram bot to begin    ║"
echo "║  📚 Commands: /help                              ║"
echo "║  💀 Self-destruct: /wipe                         ║"
echo "╚══════════════════════════════════════════════════╝"

# Keep process alive
trap "kill $C2_PID 2>/dev/null; exit" INT TERM
wait $C2_PID