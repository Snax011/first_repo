#!/bin/bash

OUTPUT_DIR="./highlights_$(date +%F)"
mkdir -p "$OUTPUT_DIR"

# Run Python processor with CSV input and video file
python3 processor.py highlights_log.csv game_video.mp4 "$OUTPUT_DIR"

# Create public/highlights directory if it doesn't exist
mkdir -p ./public/highlights

# Move clips and manifest to public folder for hosting
mv "$OUTPUT_DIR"/*.mp4 ./public/highlights/
mv "$OUTPUT_DIR"/manifest.json ./public/highlights/

echo "Highlights and manifest organized for web widget."
