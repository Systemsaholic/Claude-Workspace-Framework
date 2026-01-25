#!/bin/bash
# Framework Purity Validator
# Scans framework directory for project-specific content before pushing
#
# Usage:
#   validate-framework.sh [framework-dir]
#   validate-framework.sh              # Uses ./framework or current dir

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Determine framework directory
if [ -n "$1" ]; then
    FRAMEWORK_DIR="$1"
elif [ -d "./framework" ]; then
    FRAMEWORK_DIR="./framework"
elif [ -f "./FRAMEWORK-RULES.md" ]; then
    FRAMEWORK_DIR="."
else
    echo -e "${RED}Error: Cannot find framework directory${NC}"
    echo "Usage: validate-framework.sh [framework-dir]"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Framework Purity Validator${NC}"
echo -e "${BLUE}  Scanning: $FRAMEWORK_DIR${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Helper function for scanning
scan_files() {
    local pattern="$1"
    local description="$2"
    local severity="$3"  # error or warning

    # Search in relevant files, excluding validation scripts, .git, and .github
    local results
    results=$(grep -rn -E "$pattern" "$FRAMEWORK_DIR" \
        --include="*.md" \
        --include="*.yaml" \
        --include="*.yml" \
        --include="*.py" \
        --include="*.json" \
        --exclude="validate-framework.sh" \
        --exclude-dir=".git" \
        --exclude-dir=".github" \
        2>/dev/null || true)

    if [ -n "$results" ]; then
        if [ "$severity" = "error" ]; then
            echo -e "${RED}[ERROR]${NC} $description"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${YELLOW}[WARN]${NC} $description"
            WARNINGS=$((WARNINGS + 1))
        fi
        echo "$results" | head -10 | sed 's/^/    /'
        local count
        count=$(echo "$results" | wc -l | tr -d ' ')
        if [ "$count" -gt 10 ]; then
            echo "    ... and $((count - 10)) more matches"
        fi
        echo ""
        return 1
    fi
    return 0
}

echo -e "${BLUE}[1/7] Checking for API keys and tokens...${NC}"
scan_files 'sk_live_[A-Za-z0-9]{20,}' "Live Stripe API keys found" "error" || true
scan_files 'ghp_[A-Za-z0-9]{30,}' "GitHub personal access tokens found" "error" || true
scan_files 'gho_[A-Za-z0-9]{30,}' "GitHub OAuth tokens found" "error" || true
scan_files 'AKIA[0-9A-Z]{16}' "AWS access keys found" "error" || true

echo -e "${BLUE}[2/7] Checking for real email addresses...${NC}"
# Look for emails that aren't example.com or common placeholders
results=$(grep -rn -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$FRAMEWORK_DIR" \
    --include="*.md" \
    --include="*.yaml" \
    --include="*.yml" \
    --include="*.py" \
    --include="*.json" \
    --exclude="validate-framework.sh" \
    --exclude-dir=".git" \
    --exclude-dir=".github" \
    2>/dev/null | grep -v -E '@[a-z]+\.example\.com|@example\.com|@your-domain\.com|@yourdomain\.com|@domain\.com|@acme\.com|@placeholder|noreply@anthropic\.com|user@|admin@|test@|git@github\.com|john@|client@|jane@|rep@|support@|bdm_email|support_email' || true)

if [ -n "$results" ]; then
    echo -e "${YELLOW}[WARN]${NC} Possible real email addresses (verify these are placeholders):"
    echo "$results" | head -5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
    echo ""
fi

echo -e "${BLUE}[3/7] Checking for hardcoded IPs...${NC}"
# Look for IPs that aren't in test/private ranges or localhost
# Allowed: 192.0.2.x, 198.51.100.x, 203.0.113.x (documentation), 10.x.x.x (private), 100.64.x.x (CGNAT/Tailscale), 127.x.x.x (localhost)
results=$(grep -rn -E '\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b' "$FRAMEWORK_DIR" \
    --include="*.md" \
    --include="*.yaml" \
    --include="*.yml" \
    --include="*.py" \
    --include="*.json" \
    --exclude="validate-framework.sh" \
    --exclude-dir=".git" \
    --exclude-dir=".github" \
    2>/dev/null | grep -v -E '192\.0\.2\.|198\.51\.100\.|203\.0\.113\.|127\.|0\.0\.0\.0|255\.255\.|10\.[0-9]+\.[0-9]+\.[0-9]+|100\.64\.' || true)

if [ -n "$results" ]; then
    echo -e "${YELLOW}[WARN]${NC} Hardcoded IPs found (verify these are examples):"
    echo "$results" | head -5 | sed 's/^/    /'
    WARNINGS=$((WARNINGS + 1))
    echo ""
fi

echo -e "${BLUE}[4/7] Checking for private paths...${NC}"
scan_files '/Users/[a-zA-Z]+/' "macOS user paths found" "error" || true
scan_files '/home/[a-zA-Z]+/' "Linux user paths found" "error" || true
scan_files 'C:\\Users\\' "Windows user paths found" "error" || true

echo -e "${BLUE}[5/7] Checking for hardcoded credentials...${NC}"
scan_files 'password\s*[:=]\s*["\047][^"\047$]{3,}["\047]' "Hardcoded passwords found" "error" || true
scan_files 'secret\s*[:=]\s*["\047][^"\047$]{3,}["\047]' "Hardcoded secrets found" "error" || true

echo -e "${BLUE}[6/7] Checking for private keys...${NC}"
# Check for actual key content, not pattern references
results=$(grep -rn 'BEGIN.*PRIVATE KEY' "$FRAMEWORK_DIR" \
    --include="*.md" \
    --include="*.yaml" \
    --include="*.yml" \
    --include="*.py" \
    --include="*.pem" \
    --include="*.key" \
    --exclude="validate-framework.sh" \
    --exclude-dir=".git" \
    --exclude-dir=".github" \
    2>/dev/null | grep -v 'check_pattern\|scan_files\|echo\|#' || true)

if [ -n "$results" ]; then
    echo -e "${RED}[ERROR]${NC} Private keys found:"
    echo "$results" | head -5 | sed 's/^/    /'
    ERRORS=$((ERRORS + 1))
    echo ""
fi

echo -e "${BLUE}[7/7] Checking for sensitive files...${NC}"
SENSITIVE_FILES=$(find "$FRAMEWORK_DIR" -type f \( \
    -name ".env" -o \
    -name ".env.local" -o \
    -name ".env.production" -o \
    -name "*.pem" -o \
    -name "*.key" -o \
    -name "id_rsa" -o \
    -name "id_ed25519" -o \
    -name "credentials.json" -o \
    -name "secrets.yaml" -o \
    -name "secrets.yml" \
    \) ! -name ".env.example" 2>/dev/null || true)

if [ -n "$SENSITIVE_FILES" ]; then
    echo -e "${RED}[ERROR]${NC} Sensitive files found:"
    echo "$SENSITIVE_FILES" | sed 's/^/    /'
    ERRORS=$((ERRORS + 1))
    echo ""
fi

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Framework is clean - safe to push${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found - review before pushing${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s) - DO NOT PUSH${NC}"
    echo ""
    echo "Fix the errors above before pushing to the framework repo."
    echo "See FRAMEWORK-RULES.md for guidelines."
    exit 1
fi
