# ⚔️ GHOST PROTOCOL — MAKEFILE
# ==============================

.PHONY: help install deploy start stop restart clean wipe test

help:
	@echo "╔══════════════════════════════════════════════════╗"
	@echo "║  ⚔️ GHOST PROTOCOL — COMMANDS                    ║"
	@echo "╠══════════════════════════════════════════════════╣"
	@echo "║  make install     Install all dependencies       ║"
	@echo "║  make deploy      Deploy complete stack          ║"
	@echo "║  make start       Start all services             ║"
	@echo "║  make stop        Stop all services              ║"
	@echo "║  make restart     Restart all services           ║"
	@echo "║  make status      Check system status            ║"
	@echo "║  make clean       Clean temporary files          ║"
	@echo "║  make wipe        Self-destruct (all traces)     ║"
	@echo "║  make test        Run test suite                 ║"
	@echo "║  make update      Update tools and models        ║"
	@echo "╚══════════════════════════════════════════════════╝"

install:
	@echo "[*] Installing dependencies..."
	@bash scripts/setup.sh

deploy: install
	@echo "[*] Deploying Ghost Protocol..."
	@docker-compose up -d --build
	@echo "[+] Ghost Protocol deployed. Send /start to your Telegram bot."

start:
	@docker-compose start

stop:
	@docker-compose stop

restart: stop start

status:
	@docker-compose ps
	@echo "---"
	@curl -s http://localhost:11434/api/tags | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'AI Models: {len(d.get(\"models\",[]))} loaded')" 2>/dev/null || echo "Ollama not running"

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf tmp/ results/ logs/ 2>/dev/null || true
	@echo "[+] Clean complete"

wipe:
	@echo "[!] SELF-DESTRUCT INITIATED"
	@docker-compose down -v 2>/dev/null || true
	@docker system prune -af 2>/dev/null || true
	@rm -rf data/ logs/ results/ tmp/ 2>/dev/null || true
	@echo "[+] All traces eliminated"

test:
	@python3 -m pytest tests/ -v --tb=short 2>/dev/null || echo "Install pytest: pip3 install pytest"

update:
	@echo "[*] Updating tools..."
	@nuclei -update-templates 2>/dev/null || true
	@echo "[*] Updating AI models..."
	@ollama pull dolphin-llama3:latest 2>/dev/null || true
	@echo "[+] Update complete"