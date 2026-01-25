#!/bin/bash
# Install Git Hooks for Framework Protection
#
# This script installs pre-push hooks that validate framework purity
# before allowing pushes to the upstream framework repo.
#
# Usage:
#   ./install-hooks.sh           # Install in current repo
#   ./install-hooks.sh /path     # Install in specified repo

set -e

REPO_DIR="${1:-.}"
HOOKS_DIR="$REPO_DIR/.git/hooks"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing framework protection hooks...${NC}"

# Ensure .git/hooks exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: $HOOKS_DIR not found. Is this a git repository?"
    exit 1
fi

# Create pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'HOOK_EOF'
#!/bin/bash
# Pre-push hook: Validate framework purity before pushing
#
# This hook runs when pushing to a remote named "framework"
# and validates that no project-specific content is being pushed.

# Only validate when pushing to framework remote
remote="$1"
url="$2"

# Check if this is a push to the framework remote
if [[ "$remote" == "framework" ]] || [[ "$url" == *"Claude-Workspace-Framework"* ]]; then
    echo "Validating framework purity before push..."

    # Find the validate script
    VALIDATE_SCRIPT=""
    if [ -f "./framework/scripts/validate-framework.sh" ]; then
        VALIDATE_SCRIPT="./framework/scripts/validate-framework.sh"
        FRAMEWORK_DIR="./framework"
    elif [ -f "./scripts/validate-framework.sh" ]; then
        VALIDATE_SCRIPT="./scripts/validate-framework.sh"
        FRAMEWORK_DIR="."
    fi

    if [ -n "$VALIDATE_SCRIPT" ]; then
        if ! bash "$VALIDATE_SCRIPT" "$FRAMEWORK_DIR"; then
            echo ""
            echo "Push blocked: Framework validation failed"
            echo "Fix the issues above before pushing."
            exit 1
        fi
    else
        echo "Warning: validate-framework.sh not found, skipping validation"
    fi
fi

exit 0
HOOK_EOF

chmod +x "$HOOKS_DIR/pre-push"

echo -e "${GREEN}✓ Pre-push hook installed${NC}"
echo ""
echo "The hook will automatically validate framework purity when pushing to:"
echo "  - Any remote named 'framework'"
echo "  - Any URL containing 'Claude-Workspace-Framework'"
echo ""
echo "To test manually, run:"
echo "  ./scripts/validate-framework.sh"
