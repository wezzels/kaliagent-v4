#!/bin/bash
# KaliAgent v4 - Security Audit Script
# Scans for exposed secrets, tokens, and sensitive information before public release

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 KaliAgent v4 - Security Audit"
echo "================================="
echo ""

ISSUES_FOUND=0

# Function to check for patterns
check_pattern() {
    local pattern=$1
    local description=$2
    local severity=$3
    
    echo -n "Checking: $description... "
    
    if grep -rn -E "$pattern" --include="*.py" --include="*.md" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.conf" --include="*.sh" . 2>/dev/null | grep -v ".git/" | grep -v "Binary file" | grep -v "security_audit.sh"; then
        echo -e "${RED}⚠️  FOUND${NC}"
        ((ISSUES_FOUND++))
    else
        echo -e "${GREEN}✅ Clean${NC}"
    fi
}

# GitHub Tokens
check_pattern "ghp_[a-zA-Z0-9]{36}" "GitHub Personal Access Token" "CRITICAL"
check_pattern "gho_[a-zA-Z0-9]{36}" "GitHub OAuth Token" "CRITICAL"
check_pattern "github_pat_[a-zA-Z0-9]{22}" "GitHub Fine-grained PAT" "CRITICAL"
check_pattern "ghr_[a-zA-Z0-9]{36}" "GitHub Release Token" "CRITICAL"

# GitLab Tokens
check_pattern "glpat-[a-zA-Z0-9]{26}" "GitLab Personal Access Token" "CRITICAL"

# AWS Credentials
check_pattern "AKIA[0-9A-Z]{16}" "AWS Access Key ID" "CRITICAL"
check_pattern "aws_secret_access_key" "AWS Secret Access Key reference" "HIGH"

# Generic Secrets
check_pattern "(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]" "Hardcoded Password" "CRITICAL"
check_pattern "(?i)(api_key|apikey|api-key)\s*[=:]\s*['\"][^'\"]{16,}['\"]" "Hardcoded API Key" "CRITICAL"
check_pattern "(?i)(secret|token)\s*[=:]\s*['\"][^'\"]{16,}['\"]" "Hardcoded Secret/Token" "CRITICAL"

# Private Keys
check_pattern "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----" "Private Key" "CRITICAL"

# Database URLs with passwords
check_pattern "(mongodb|postgres|mysql|redis)://[^:]+:[^@]+@" "Database URL with credentials" "CRITICAL"

# JWT Tokens
check_pattern "eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "JWT Token" "HIGH"

# Slack Tokens
check_pattern "xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}" "Slack Token" "CRITICAL"

# Telegram Bot Tokens
check_pattern "[0-9]+:[a-zA-Z0-9_-]{35}" "Telegram Bot Token" "HIGH"

# IP Addresses (internal network)
echo -n "Checking: Internal IP addresses (10.x.x.x)... "
if grep -rn "10\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" --include="*.py" --include="*.md" --include="*.yml" . 2>/dev/null | grep -v "localhost" | grep -v "127.0.0.1" | grep -v "10.0.100\." | grep -v "10.0.101\." | head -5; then
    echo -e "${YELLOW}⚠️  Review needed${NC}"
    echo "   (Some internal IPs found - verify they're not sensitive)"
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# Email addresses
echo -n "Checking: Email addresses... "
EMAIL_COUNT=$(grep -rn -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" --include="*.py" --include="*.md" --include="*.yml" . 2>/dev/null | grep -v ".git/" | grep -v "example.com" | grep -v "noreply" | wc -l)
if [ "$EMAIL_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $EMAIL_COUNT found${NC}"
    echo "   (Review if these should be public)"
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

# Domain names (internal)
echo -n "Checking: Internal domain names... "
if grep -rn -E "(wezzel\.com|stsgym\.com|idm\.wezzel\.com|miner|trooper[0-9]|swordfish)" --include="*.py" --include="*.md" --include="*.yml" . 2>/dev/null | grep -v ".git/" | grep -v "example.com" | head -5; then
    echo -e "${YELLOW}⚠️  Review needed${NC}"
    echo "   (Internal domain/host names found)"
else
    echo -e "${GREEN}✅ Clean${NC}"
fi

echo ""
echo "================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ SECURITY AUDIT PASSED${NC}"
    echo "No critical issues found!"
    echo ""
    echo "Ready for public release! 🚀"
    exit 0
else
    echo -e "${RED}❌ SECURITY AUDIT FAILED${NC}"
    echo "Found $ISSUES_FOUND critical issue(s)!"
    echo ""
    echo "Please review and fix the issues above before pushing to GitHub."
    exit 1
fi
