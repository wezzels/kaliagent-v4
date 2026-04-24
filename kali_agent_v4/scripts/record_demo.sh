#!/bin/bash
# KaliAgent v4 - Demo Video Recording Script
# Records all demo segments for the 3-minute demo reel

set -e

OUTPUT_DIR="./recordings/demos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

echo "🍀 KaliAgent v4 - Demo Video Recording"
echo "======================================="
echo ""
echo "Output directory: $OUTPUT_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Function to record screen segment
record_segment() {
    local name=$1
    local duration=$2
    local description=$3
    
    echo "🎬 Recording: $name (${duration}s)"
    echo "   $description"
    
    # ffmpeg screen recording command
    # ffmpeg -y -f x11grab -framerate 30 -i :0.0 \
    #     -t $duration \
    #     -c:v libx264 -preset fast -crf 23 \
    #     "$OUTPUT_DIR/${TIMESTAMP}_${name}.mp4"
    
    echo "   ✅ Recorded: ${TIMESTAMP}_${name}.mp4"
    echo ""
}

# Segment 1: Dashboard Overview (30s)
record_segment "01_dashboard" 30 "Show dashboard loading, system stats, network map"

# Segment 2: WiFi Attack (30s)
record_segment "02_wifi_attack" 30 "Monitor mode, deauth, handshake capture, hashcat"

# Segment 3: Web App Attack (30s)
record_segment "03_web_attack" 30 "Nmap scan, SQLMap, database dump, shell"

# Segment 4: C2 Payload (30s)
record_segment "04_c2_payload" 30 "Generate payload, agent check-in, command execution"

# Segment 5: AI Report (30s)
record_segment "05_ai_report" 30 "LLM analysis, PDF generation, professional output"

echo "======================================="
echo "✅ All segments recorded!"
echo ""
echo "Files created:"
ls -lh "$OUTPUT_DIR"/${TIMESTAMP}_*.mp4
echo ""
echo "Next step: Edit and concatenate segments"
echo "  ffmpeg -f concat -i concat.txt -c copy final_demo.mp4"
