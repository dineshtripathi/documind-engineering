#!/usr/bin/env bash
set -e

echo "🔍 Testing Ollama models..."

# Test Phi
echo "➡️ Phi3.5 test:"
ollama run phi3.5:3.8b-mini-instruct-q8_0 "Say hello in one short line."

# Test Llama
echo "➡️ Llama3.1 test:"
ollama run llama3.1:8b-instruct-q4_K_M "Say hello in one short line."

# Test Deepseek Coder
echo "➡️ Deepseek Coder test:"
ollama run deepseek-coder:6.7b-instruct-q8_0 "Write a single-line Python code to print Hello DocuMind."
