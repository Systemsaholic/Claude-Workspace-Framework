#!/bin/bash
# Contribute Framework Improvements
# Validates and pushes framework improvements to upstream repository
#
# Usage:
#   contribute-framework.sh                    # Interactive mode
#   contribute-framework.sh "description"     # With commit message
#   contribute-framework.sh --check           # Dry run (validate only)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

FRAMEWORK_DIR="${FRAMEWORK_DIR:-./framework}"
FRAMEWORK_REMOTE="${FRAMEWORK_REMOTE:-framework}"
DESCRIPTION="${1:-}"
DRY_RUN=false

if [ "$1" = "--check" ] || [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    DESCRIPTION=""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Contribute Framework Improvements${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${CYAN}[1/5] Checking prerequisites...${NC}"

if [ ! -d "$FRAMEWORK_DIR" ]; then
    echo -e "${RED}Error: Framework directory not found at $FRAMEWORK_DIR${NC}"
    echo "Make sure you're in a workspace with the framework subtree."
    exit 1
fi

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

if ! git remote get-url "$FRAMEWORK_REMOTE" > /dev/null 2>&1; then
    echo -e "${RED}Error: Framework remote '$FRAMEWORK_REMOTE' not configured${NC}"
    echo ""
    echo "Add it with:"
    echo "  git remote add $FRAMEWORK_REMOTE https://github.com/YOUR_ORG/Claude-Workspace-Framework.git"
    exit 1
fi

REMOTE_URL=$(git remote get-url "$FRAMEWORK_REMOTE")
echo -e "  Remote: ${GREEN}$FRAMEWORK_REMOTE${NC} → $REMOTE_URL"
echo ""

# Step 2: Check for changes
echo -e "${CYAN}[2/5] Detecting framework changes...${NC}"

CHANGED_FILES=$(git diff --name-only "$FRAMEWORK_DIR/" 2>/dev/null || true)
STAGED_FILES=$(git diff --cached --name-only "$FRAMEWORK_DIR/" 2>/dev/null || true)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard "$FRAMEWORK_DIR/" 2>/dev/null || true)

ALL_CHANGES="$CHANGED_FILES"$'\n'"$STAGED_FILES"$'\n'"$UNTRACKED_FILES"
ALL_CHANGES=$(echo "$ALL_CHANGES" | sort -u | grep -v '^$' || true)

if [ -z "$ALL_CHANGES" ]; then
    echo -e "${YELLOW}No changes detected in framework directory.${NC}"
    echo ""
    echo "Make changes to files in $FRAMEWORK_DIR/ before contributing."
    exit 0
fi

echo -e "  ${GREEN}Modified files:${NC}"
echo "$ALL_CHANGES" | sed 's/^/    /'
echo ""

# Step 3: Validate purity
echo -e "${CYAN}[3/5] Validating framework purity...${NC}"

VALIDATOR="$FRAMEWORK_DIR/scripts/validate-framework.sh"
if [ -f "$VALIDATOR" ]; then
    if ! bash "$VALIDATOR" "$FRAMEWORK_DIR"; then
        echo ""
        echo -e "${RED}Framework validation failed!${NC}"
        echo "Fix the issues above before contributing."
        echo "See $FRAMEWORK_DIR/FRAMEWORK-RULES.md for guidelines."
        exit 1
    fi
else
    echo -e "${YELLOW}Warning: Validator not found, skipping purity check${NC}"
fi
echo ""

# Step 4: Show diff
echo -e "${CYAN}[4/5] Changes to contribute:${NC}"
echo ""

git diff --stat "$FRAMEWORK_DIR/" 2>/dev/null || true
echo ""

if [ -n "$UNTRACKED_FILES" ]; then
    echo -e "  ${GREEN}New files:${NC}"
    echo "$UNTRACKED_FILES" | sed 's/^/    + /'
    echo ""
fi

# Show detailed diff (abbreviated)
echo -e "  ${BLUE}Detailed changes:${NC}"
git diff "$FRAMEWORK_DIR/" 2>/dev/null | head -100
DIFF_LINES=$(git diff "$FRAMEWORK_DIR/" 2>/dev/null | wc -l)
if [ "$DIFF_LINES" -gt 100 ]; then
    echo "  ... ($((DIFF_LINES - 100)) more lines)"
fi
echo ""

# Dry run stops here
if [ "$DRY_RUN" = true ]; then
    echo -e "${GREEN}✓ Dry run complete - framework is ready to contribute${NC}"
    echo ""
    echo "Run without --check to actually push changes."
    exit 0
fi

# Step 5: Confirm and push
echo -e "${CYAN}[5/5] Ready to contribute${NC}"
echo ""

if [ -z "$DESCRIPTION" ]; then
    echo -e "Enter a description for this improvement:"
    read -r DESCRIPTION
    if [ -z "$DESCRIPTION" ]; then
        echo -e "${RED}Description required${NC}"
        exit 1
    fi
fi

echo ""
echo -e "Description: ${GREEN}$DESCRIPTION${NC}"
echo ""
echo -e "${YELLOW}This will push changes to the upstream framework repository.${NC}"
echo -e "Other workspaces will be able to pull these improvements."
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Committing and pushing...${NC}"

# Stage framework changes
git add "$FRAMEWORK_DIR/"

# Get workspace name for attribution
WORKSPACE_NAME=$(basename "$(pwd)")

# Commit
git commit -m "$(cat <<EOF
Improve framework: $DESCRIPTION

Contributed from workspace: $WORKSPACE_NAME

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Push to upstream
echo ""
echo -e "${BLUE}Pushing to upstream framework...${NC}"
git subtree push --prefix="$FRAMEWORK_DIR" "$FRAMEWORK_REMOTE" main

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ Framework improvement contributed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Other workspaces can pull this improvement with:"
echo "  ./framework/scripts/framework-sync.sh pull"
echo ""
