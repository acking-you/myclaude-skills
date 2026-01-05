#!/bin/bash
# Droid custom model configuration script

set -e

SETTINGS_FILE="$HOME/.factory/settings.json"

show_help() {
    cat << EOF
Usage: $0 -u <baseurl> -m <model> -k <api_key> [options]

Required:
  -u, --url       Base URL of the API provider
  -m, --model     Model name (auto-detects provider from name)
  -k, --key       API key/token

Options:
  -n, --name      Display name (default: auto-generated)
  -t, --thinking  Enable thinking mode with budget tokens (default: 10000, 0 to disable)
  -h, --help      Show this help

Provider auto-detection:
  - claude-*  -> anthropic
  - gpt-*     -> openai
  - others    -> generic-chat-completion-api

Documentation:
  Settings:     https://docs.factory.ai/cli/configuration/settings
  BYOK:         https://docs.factory.ai/cli/byok/overview
  Full docs:    https://docs.factory.ai/factory-docs-map.md

Examples:
  $0 -u https://api.example.com/ -m claude-opus-4-5-20251101 -k sk-xxx
  $0 -u https://api.openai.com/v1 -m gpt-4o -k sk-xxx -t 0
EOF
}

detect_provider() {
    local model="$1"
    case "$model" in
        claude-*) echo "anthropic" ;;
        gpt-*)    echo "openai" ;;
        *)        echo "generic-chat-completion-api" ;;
    esac
}

BASE_URL=""
MODEL=""
API_KEY=""
DISPLAY_NAME=""
THINKING_BUDGET=10000

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)      BASE_URL="$2"; shift 2 ;;
        -m|--model)    MODEL="$2"; shift 2 ;;
        -k|--key)      API_KEY="$2"; shift 2 ;;
        -n|--name)     DISPLAY_NAME="$2"; shift 2 ;;
        -t|--thinking) THINKING_BUDGET="$2"; shift 2 ;;
        -h|--help)     show_help; exit 0 ;;
        *)             echo "Unknown option: $1"; show_help; exit 1 ;;
    esac
done

if [[ -z "$BASE_URL" || -z "$MODEL" || -z "$API_KEY" ]]; then
    echo "Error: -u, -m, -k are required"
    show_help
    exit 1
fi

PROVIDER=$(detect_provider "$MODEL")
[[ -z "$DISPLAY_NAME" ]] && DISPLAY_NAME="$MODEL"

mkdir -p "$(dirname "$SETTINGS_FILE")"

if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo '{}' > "$SETTINGS_FILE"
fi

if [[ "$THINKING_BUDGET" -gt 0 && "$PROVIDER" == "anthropic" ]]; then
    EXTRA_ARGS='"extraArgs":{"thinking":{"type":"enabled","budget_tokens":'"$THINKING_BUDGET"'}},'
else
    EXTRA_ARGS=""
fi

NEW_MODEL=$(cat << EOF
{
  "model": "$MODEL",
  "displayName": "$DISPLAY_NAME",
  "baseUrl": "$BASE_URL",
  "apiKey": "$API_KEY",
  "provider": "$PROVIDER",
  "supportsImages": true,
  $EXTRA_ARGS
  "noImageSupport": false
}
EOF
)

if command -v jq &> /dev/null; then
    NEW_MODEL_JSON=$(echo "$NEW_MODEL" | jq -c '.')
    jq --argjson model "$NEW_MODEL_JSON" '.customModels = (.customModels // []) + [$model]' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp"
    mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"
else
    echo "Warning: jq not found, manual JSON editing required"
    echo "Add this to customModels array in $SETTINGS_FILE:"
    echo "$NEW_MODEL"
    exit 1
fi

echo "Added custom model:"
echo "  Model:    $MODEL"
echo "  Provider: $PROVIDER"
echo "  URL:      $BASE_URL"
echo "  Name:     $DISPLAY_NAME"
[[ "$THINKING_BUDGET" -gt 0 && "$PROVIDER" == "anthropic" ]] && echo "  Thinking: enabled ($THINKING_BUDGET tokens)"
echo ""
echo "Use '/model' in droid to select it."
