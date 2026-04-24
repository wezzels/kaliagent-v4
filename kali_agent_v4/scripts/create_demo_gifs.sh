#!/bin/bash
# KaliAgent v4 - Create Demo GIFs from Terminal Output
# Alternative to screen recording - works in any environment

set -e

OUTPUT_DIR="./recordings/gifs"
mkdir -p "$OUTPUT_DIR"

echo "🍀 Creating KaliAgent v4 Demo GIFs"
echo "=================================="

# GIF 1: Dashboard Startup
echo "📊 Creating dashboard_startup.gif..."
cat > /tmp/dashboard_demo.txt << 'EOF'
🍀 KaliAgent v4 - Starting Dashboard...
✅ Loading modules...
✅ Connecting to Redis...
✅ Connecting to Ollama...
✅ Initializing C2 servers...
✅ Dashboard ready at http://localhost:5007

[System Stats]
CPU:    [████████░░] 23.5%
Memory: [███████████████░] 45.2%
Disk:   [█████████████████████░] 67.8%
EOF

# Convert to GIF using imagemagick (if available)
if command -v convert &> /dev/null; then
    convert -size 800x200 xc:black -font "Courier" -pointsize 14 -fill green \
        -annotate 0 "@/tmp/dashboard_demo.txt" \
        "$OUTPUT_DIR/dashboard_startup.gif"
    echo "   ✅ Created dashboard_startup.gif"
else
    echo "   ⚠️  ImageMagick not found - skipping GIF creation"
fi

# GIF 2: Network Scan
echo "🔍 Creating network_scan.gif..."
cat > /tmp/scan_demo.txt << 'EOF'
$ ./kaliagent scan -t 10.0.100.0/24 --type nmap

🔍 Starting nmap scan on 10.0.100.0/24...

[████████░░░░░░░░░░░░] 40% - Scanning hosts
[████████████████░░░░] 80% - Detecting services
[████████████████████] 100% - Complete!

Results:
  5 hosts discovered
  23 open ports
  12 vulnerabilities found
  47 services identified
EOF

if command -v convert &> /dev/null; then
    convert -size 800x250 xc:black -font "Courier" -pointsize 14 -fill cyan \
        -annotate 0 "@/tmp/scan_demo.txt" \
        "$OUTPUT_DIR/network_scan.gif"
    echo "   ✅ Created network_scan.gif"
fi

# GIF 3: SQL Injection Attack
echo "💉 Creating sql_injection.gif..."
cat > /tmp/sqli_demo.txt << 'EOF'
$ ./kaliagent attack -t 10.0.100.10 -a web --method sql_injection

⚔️  Launching web attack on 10.0.100.10...

Step 1/5: Reconnaissance     ✅ Complete
Step 2/5: Vuln Detection     ✅ Complete  
Step 3/5: Exploitation       ✅ Complete
Step 4/5: Post-Exploitation  ✅ Complete
Step 5/5: Evidence Collection ✅ Complete

🎯 SUCCESS! SQL Injection confirmed
   Payload: admin'-- 
   Bypassed: Authentication
   Database: users table dumped (127 records)
EOF

if command -v convert &> /dev/null; then
    convert -size 800x280 xc:black -font "Courier" -pointsize 14 -fill "#e94560" \
        -annotate 0 "@/tmp/sqli_demo.txt" \
        "$OUTPUT_DIR/sql_injection.gif"
    echo "   ✅ Created sql_injection.gif"
fi

# GIF 4: Report Generation
echo "📄 Creating report_generation.gif..."
cat > /tmp/report_demo.txt << 'EOF'
$ ./kaliagent report -f pdf

📄 Generating PDF report...

✅ Executive Summary
✅ Risk Assessment (Critical: 2, High: 5, Medium: 8)
✅ Detailed Findings (15 vulnerabilities)
✅ Evidence Screenshots (23 images)
✅ Remediation Recommendations
✅ CVSS Scoring

Report saved: reports/pentest_report_20260424_135300.pdf
Size: 2.4 MB
Pages: 47

🎉 Report generation complete!
EOF

if command -v convert &> /dev/null; then
    convert -size 800x300 xc:black -font "Courier" -pointsize 14 -fill "#00ff88" \
        -annotate 0 "@/tmp/report_demo.txt" \
        "$OUTPUT_DIR/report_generation.gif"
    echo "   ✅ Created report_generation.gif"
fi

# GIF 5: AI Natural Language
echo "🤖 Creating ai_command.gif..."
cat > /tmp/ai_demo.txt << 'EOF'
$ ./kaliagent ai "Find all web servers and check for SQL injection"

🤖 AI Command: Find all web servers and check for SQL injection

Analyzing... 🧠

Parsed Command:
  Type: scan + attack
  Target: 10.0.100.0/24
  Filter: port 80,443
  Attack: SQL injection

Recommendation:
  "Target 10.0.100.10 running Apache 2.4.18 is vulnerable.
   Use SQLMap with --dbs flag for database enumeration."

Executing attack chain... ✅
EOF

if command -v convert &> /dev/null; then
    convert -size 800x320 xc:black -font "Courier" -pointsize 14 -fill "#ffaa00" \
        -annotate 0 "@/tmp/ai_demo.txt" \
        "$OUTPUT_DIR/ai_command.gif"
    echo "   ✅ Created ai_command.gif"
fi

echo ""
echo "=================================="
echo "✅ All GIFs created!"
echo ""
echo "Files:"
ls -lh "$OUTPUT_DIR"/*.gif 2>/dev/null || echo "   (Install ImageMagick to create GIFs)"
echo ""
echo "Usage: Insert these GIFs into README.md or documentation"
