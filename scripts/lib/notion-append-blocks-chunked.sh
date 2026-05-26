#!/bin/bash

# Notion Append Blocks Script - Chunked Version
# 将Markdown内容分块追加到Notion页面

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

# Function to split content into chunks under 2000 characters
split_into_chunks() {
    local input_file="$1"
    local temp_dir="/tmp/notion_chunks_$(date +%s)"
    mkdir -p "$temp_dir"
    
    local current_chunk=0
    local current_content=""
    local line_count=0
    
    while IFS= read -r line; do
        # Skip empty lines that would become paragraph separators
        if [[ "$line" =~ ^$ ]]; then
            continue
        fi
        
        # Add line to current content
        if [ -n "$current_content" ]; then
            current_content="$current_content\n$line"
        else
            current_content="$line"
        fi
        
        # If content exceeds 1800 characters, write to file and start new chunk
        if [ ${#current_content} -gt 1800 ]; then
            echo -e "$current_content" > "$temp_dir/chunk_$current_chunk.txt"
            current_chunk=$((current_chunk + 1))
            current_content="$line"
            line_count=1
        else
            line_count=$((line_count + 1))
        fi
        
        # Start new chunk after 5 lines to keep content manageable
        if [ $line_count -gt 5 ]; then
            echo -e "$current_content" > "$temp_dir/chunk_$current_chunk.txt"
            current_chunk=$((current_chunk + 1))
            current_content=""
            line_count=0
        fi
    done < "$input_file"
    
    # Write any remaining content
    if [ -n "$current_content" ]; then
        echo -e "$current_content" > "$temp_dir/chunk_$current_chunk.txt"
    fi
    
    echo "$temp_dir"
}

echo "Splitting content into chunks..."
TEMP_DIR=$(split_into_chunks "$MARKDOWN_FILE")

# Count chunks
CHUNK_COUNT=$(ls -1 "$TEMP_DIR"/*.txt | wc -l)

echo "Found $CHUNK_COUNT chunks to append..."

# Append each chunk
CHUNK_SUCCESS=0
for chunk_file in "$TEMP_DIR"/*.txt; do
    if notion-cli block append "$PAGE_ID" --content "$(cat "$chunk_file")"; then
        echo "Chunk $(basename "$chunk_file") appended successfully"
        CHUNK_SUCCESS=$((CHUNK_SUCCESS + 1))
        # Add small delay between requests to avoid rate limiting
        sleep 0.5
    else
        echo "Error appending chunk $(basename "$chunk_file")"
    fi
done

# Clean up
rm -rf "$TEMP_DIR"

if [ "$CHUNK_SUCCESS" -gt 0 ]; then
    echo "Successfully appended $CHUNK_SUCCESS chunks to Notion page"
    echo "PAGE_ID:$PAGE_ID"
    exit 0
else
    echo "Failed to append any chunks"
    exit 1
fi