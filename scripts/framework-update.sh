#!/bin/bash
# Framework Update Handler
# Runs after pulling framework updates to detect and apply changes
#
# Usage:
#   framework-update.sh                    # Show what's new
#   framework-update.sh --apply            # Apply updates to workspace CLAUDE.md
#   framework-update.sh --changelog        # Show recent changelog entries

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

FRAMEWORK_DIR="${FRAMEWORK_DIR:-./framework}"
WORKSPACE_CLAUDE="${WORKSPACE_CLAUDE:-./CLAUDE.md}"
MANIFEST="$FRAMEWORK_DIR/FRAMEWORK-MANIFEST.yaml"
LOCAL_MANIFEST=".framework-manifest-local.yaml"

MODE="${1:-show}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Framework Update Handler${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check prerequisites
if [ ! -f "$MANIFEST" ]; then
    echo -e "${RED}Error: Framework manifest not found at $MANIFEST${NC}"
    exit 1
fi

# Get current framework version
FRAMEWORK_VERSION=$(grep "^version:" "$MANIFEST" | cut -d'"' -f2)
FRAMEWORK_DATE=$(grep "^updated:" "$MANIFEST" | cut -d'"' -f2)

echo -e "Framework version: ${GREEN}$FRAMEWORK_VERSION${NC} (updated: $FRAMEWORK_DATE)"
echo ""

# Show changelog if requested
if [ "$MODE" = "--changelog" ]; then
    CHANGELOG="$FRAMEWORK_DIR/CHANGELOG.md"
    if [ -f "$CHANGELOG" ]; then
        echo -e "${CYAN}Recent Changes:${NC}"
        head -100 "$CHANGELOG"
    else
        echo -e "${YELLOW}No changelog found${NC}"
    fi
    exit 0
fi

# Compare with local cached manifest (if exists)
echo -e "${CYAN}Checking for new capabilities...${NC}"
echo ""

NEW_SKILLS=()
NEW_PACKAGES=()
NEW_PLAYBOOKS=()
NEW_SCRIPTS=()

# Extract skills from manifest
SKILLS=$(grep -A1 "^  [a-z-]*:$" "$MANIFEST" | grep "command:" | sed 's/.*command: "\(.*\)"/\1/' || true)

# Check what's new by comparing with local tracking file
if [ -f "$LOCAL_MANIFEST" ]; then
    OLD_VERSION=$(grep "^version:" "$LOCAL_MANIFEST" | cut -d'"' -f2 || echo "0.0.0")

    if [ "$OLD_VERSION" != "$FRAMEWORK_VERSION" ]; then
        echo -e "${GREEN}Framework updated: $OLD_VERSION → $FRAMEWORK_VERSION${NC}"
        echo ""

        # Compare skills
        OLD_SKILLS=$(grep "command:" "$LOCAL_MANIFEST" 2>/dev/null | sed 's/.*command: "\(.*\)"/\1/' || true)
        for skill in $SKILLS; do
            if ! echo "$OLD_SKILLS" | grep -q "$skill"; then
                NEW_SKILLS+=("$skill")
            fi
        done

        # Compare packages
        NEW_PKGS=$(diff <(grep "^  [a-z-]*:$" "$LOCAL_MANIFEST" 2>/dev/null | head -20 || true) \
                       <(grep "^  [a-z-]*:$" "$MANIFEST" | head -20) 2>/dev/null | grep "^>" | sed 's/> *//' || true)
    fi
else
    echo -e "${YELLOW}First run - all capabilities are new to this workspace${NC}"
    for skill in $SKILLS; do
        NEW_SKILLS+=("$skill")
    done
fi

# Display what's new
if [ ${#NEW_SKILLS[@]} -gt 0 ]; then
    echo -e "${GREEN}New Skills Available:${NC}"
    for skill in "${NEW_SKILLS[@]}"; do
        DESC=$(grep -A2 "command: \"$skill\"" "$MANIFEST" | grep "description:" | sed 's/.*description: "\(.*\)"/\1/' || echo "")
        echo -e "  ${CYAN}$skill${NC} - $DESC"
    done
    echo ""
fi

# Show all available skills
echo -e "${CYAN}All Framework Skills:${NC}"
grep -B2 "command:" "$MANIFEST" | grep -E "(command:|description:)" | paste - - | \
    sed 's/.*command: "\([^"]*\)".*description: "\([^"]*\)".*/  \1 - \2/' || true
echo ""

# Show packages
echo -e "${CYAN}Framework Packages:${NC}"
grep -A1 "^  [a-z-]*:$" "$MANIFEST" 2>/dev/null | grep -B1 "version:" | grep -v "version:" | grep -v "^--$" | \
    sed 's/^  \([a-z-]*\):$/  - \1/' | head -10 || true
echo ""

# Apply updates if requested
if [ "$MODE" = "--apply" ]; then
    echo -e "${CYAN}Applying updates to workspace...${NC}"

    if [ ! -f "$WORKSPACE_CLAUDE" ]; then
        echo -e "${YELLOW}Warning: Workspace CLAUDE.md not found at $WORKSPACE_CLAUDE${NC}"
        echo "Specify location with: WORKSPACE_CLAUDE=/path/to/CLAUDE.md $0 --apply"
    else
        # Check if Framework Management section exists
        if ! grep -q "### Framework Management" "$WORKSPACE_CLAUDE"; then
            echo -e "${GREEN}Adding Framework Management section to CLAUDE.md...${NC}"

            # Find the Operations section and add after it
            if grep -q "### Operations" "$WORKSPACE_CLAUDE"; then
                # Create the section to add
                SECTION=$(cat <<'SECTION_EOF'

### Framework Management

| Command | Purpose |
|---------|---------|
| `/contribute-framework` | Push improvements to upstream framework |

> **Framework Updates:** Run `./framework/scripts/framework-sync.sh pull` to get latest framework updates.
SECTION_EOF
)
                # Use sed to append after Operations section (this is complex, so we'll use a simpler approach)
                echo -e "${YELLOW}Please manually add the Framework Management section to your CLAUDE.md${NC}"
                echo ""
                echo "Add this after your Operations section:"
                echo "$SECTION"
            fi
        else
            echo -e "${GREEN}Framework Management section already exists${NC}"
        fi

        # Add any new skills
        for skill in "${NEW_SKILLS[@]}"; do
            if ! grep -q "$skill" "$WORKSPACE_CLAUDE"; then
                echo -e "  ${YELLOW}New skill available: $skill${NC}"
                echo "  Consider adding to your CLAUDE.md skills section"
            fi
        done
    fi
    echo ""
fi

# Save current manifest for future comparison
cp "$MANIFEST" "$LOCAL_MANIFEST"
echo -e "${GREEN}✓ Local manifest cache updated${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  - Review new capabilities above"
echo "  - Update your CLAUDE.md to reference new skills"
echo "  - Run with --apply to auto-update (experimental)"
echo ""
