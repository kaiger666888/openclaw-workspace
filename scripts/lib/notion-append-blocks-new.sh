#!/bin/bash

# Notion Append Blocks Script
# 将Markdown内容追加到Notion页面

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <PAGE_ID> <MARKDOWN_FILE>"
    exit 1
fi

PAGE_ID="$1"
MARKDOWN_FILE="$2"

if [ ! -f "$MARKDOWN_FILE" ]; then
    echo "Error: File does not exist: $MARKDOWN_FILE"
    exit 1
fi

if ! command -v notion-cli >/dev/null 2>&1; then
    echo "Error: notion-cli is not installed or not in PATH"
    exit 1
fi

echo "Converting Markdown format..."

# Create a temporary file with the content
TEMP_FILE="/tmp/startup_failures_$(date +%s).txt"
cp "$MARKDOWN_FILE" "$TEMP_FILE"

echo "Appending content to Notion page $PAGE_ID..."

if notion-cli block append "$PAGE_ID" --content "$(cat "$TEMP_FILE")"; then
    echo "Content appended successfully"
    rm -f "$TEMP_FILE"
    echo "PAGE_ID:$PAGE_ID"
    exit 0
else
    echo "Error: Content append failed"
    rm -f "$TEMP_FILE"
    exit 1
fi