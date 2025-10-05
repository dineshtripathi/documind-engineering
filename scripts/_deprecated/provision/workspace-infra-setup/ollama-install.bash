curl -fsSL https://ollama.com/install.sh | sh

curl -fsSL https://ollama.com/install.sh | sh
which ollama
ollama --version
ollama serve &

ollama pull phi3.5:3.8b-mini-instruct-q8_0
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull deepseek-coder:6.7b-instruct-q8_0
ollama run phi3.5:3.8b-mini-instruct-q8_0 -p "Hello from DocuMind Hybrid!"

ollama pull phi3.5:3.8b-mini-instruct-q8_0
ollama pull llama3.1:8b-instruct-q4_K_M

#--- Full setup script ---with fixes

# Update to latest Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or if you prefer manual:
sudo systemctl stop ollama
curl -L https://ollama.ai/download/ollama-linux-amd64 -o /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama
sudo systemctl start ollama

# --- Full setup script ---
pkill -f "ollama serve" || true
# one-off for this shell:
OLLAMA_HOST=127.0.0.1:11435 nohup ollama serve >/tmp/ollama.log 2>&1 &

# verify server version on 11435:
curl -s http://127.0.0.1:11435/api/version
export OLLAMA_HOST=127.0.0.1:11435
echo 'export OLLAMA_HOST=127.0.0.1:11435' >> ~/.bashrc

ollama --version
curl -s http://127.0.0.1:11435/api/version
ollama pull phi3.5:3.8b-mini-instruct-q8_0
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull deepseek-coder:6.7b-instruct-q8_0
