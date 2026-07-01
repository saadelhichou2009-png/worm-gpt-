#!/bin/bash
# ⚔️ GHOST PROTOCOL — SETUP SCRIPT
# =================================
# Complete system setup on fresh Oracle Cloud instance

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║  ⚔️ GHOST PROTOCOL SETUP                         ║"
echo "╚══════════════════════════════════════════════════╝"

# === Step 1: System Updates ===
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# === Step 2: Install Dependencies ===
echo "[2/8] Installing dependencies..."
sudo apt install -y \
    docker.io \
    docker-compose \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    nmap \
    masscan \
    netcat-openbsd \
    dnsutils \
    hydra \
    jq \
    tmux \
    htop \
    sqlite3 \
    redis-tools \
    cron

# === Step 3: Install Python Packages ===
echo "[3/8] Installing Python packages..."
pip3 install --no-cache-dir \
    requests \
    aiohttp \
    httpx \
    cryptography \
    PyJWT \
    pyyaml \
    beautifulsoup4 \
    redis \
    psutil \
    colorama \
    tqdm \
    rich \
    python-dotenv \
    jinja2 \
    pytest

# === Step 4: Install Ollama ===
echo "[4/8] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Wait for Ollama to start
sleep 5

# === Step 5: Download AI Models ===
echo "[5/8] Downloading uncensored AI models..."
ollama pull dolphin-llama3:latest &
ollama pull wizardlm-uncensored:latest &
wait

# === Step 6: Install Pentesting Tools ===
echo "[6/8] Installing pentesting tools..."

# Nuclei
wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_arm64.tar.gz -O /tmp/nuclei.tar.gz
sudo tar -xzf /tmp/nuclei.tar.gz -C /usr/local/bin/ nuclei
nuclei -update-templates 2>/dev/null || true

# httpx
wget -q https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_linux_arm64.tar.gz -O /tmp/httpx.tar.gz
sudo tar -xzf /tmp/httpx.tar.gz -C /usr/local/bin/ httpx

# === Step 7: Configure Docker ===
echo "[7/8] Configuring Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Pull Docker images (in background)
docker pull ollama/ollama:latest &
docker pull python:3.12-alpine &
docker pull instrumentisto/nmap:latest &
docker pull projectdiscovery/nuclei:latest &
docker pull dperson/torproxy:latest &
docker pull redis:alpine &
wait

# === Step 8: Final Configuration ===
echo "[8/8] Final configuration..."

# Create directories
mkdir -p ~/ghost-protocol/{config,core,storage,queue,auth,sandbox,adapters,agents,templates,results}

# Set up cron jobs
(crontab -l 2>/dev/null; echo "0 */6 * * * nuclei -update-templates 2>&1 | logger -t ghost-update") | crontab -
(crontab -l 2>/dev/null; echo "0 0 * * * find /tmp -name 'sqlmap*' -mtime +1 -delete 2>/dev/null") | crontab -

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE                               ║"
echo "║                                                  ║"
echo "║  Next steps:                                     ║"
echo "║  1. cp .env.example .env                         ║"
echo "║  2. Edit .env with your Telegram token           ║"
echo "║  3. make deploy                                  ║"
echo "║  4. Send /start to your Telegram bot             ║"
echo "╚══════════════════════════════════════════════════╝"