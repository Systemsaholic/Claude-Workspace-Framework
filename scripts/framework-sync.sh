#!/bin/bash
# Framework Sync Script
# Manages subtree operations for Claude Workspace Framework
#
# Usage:
#   framework-sync.sh pull    - Pull latest framework updates
#   framework-sync.sh push    - Push framework improvements upstream
#   framework-sync.sh status  - Show framework sync status
#   framework-sync.sh init    - Initialize framework subtree in a new project

set -e

FRAMEWORK_REMOTE="${FRAMEWORK_REMOTE:-framework}"
FRAMEWORK_PREFIX="${FRAMEWORK_PREFIX:-framework}"
FRAMEWORK_BRANCH="${FRAMEWORK_BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    cat << EOF
Framework Sync - Manage Claude Workspace Framework subtree

COMMANDS:
    pull      Pull latest framework updates from upstream
    push      Push framework improvements back to upstream
    status    Show current framework sync status
    init      Initialize framework subtree (for new projects)
    diff      Show changes in framework directory

ENVIRONMENT VARIABLES:
    FRAMEWORK_REMOTE   Git remote name (default: framework)
    FRAMEWORK_PREFIX   Subtree prefix path (default: framework)
    FRAMEWORK_BRANCH   Branch to sync (default: main)

EXAMPLES:
    # Pull latest framework updates
    ./framework-sync.sh pull

    # Push your improvements back
    ./framework-sync.sh push

    # Initialize in a new project
    FRAMEWORK_REMOTE=https://github.com/Systemsaholic/Claude-Workspace-Framework.git
    ./framework-sync.sh init

EOF
}

check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}

check_remote() {
    if ! git remote get-url "$FRAMEWORK_REMOTE" > /dev/null 2>&1; then
        print_error "Remote '$FRAMEWORK_REMOTE' not found"
        print_status "Add it with: git remote add $FRAMEWORK_REMOTE <framework-repo-url>"
        exit 1
    fi
}

cmd_pull() {
    check_git_repo
    check_remote

    print_status "Fetching from $FRAMEWORK_REMOTE..."
    git fetch "$FRAMEWORK_REMOTE"

    print_status "Pulling framework updates into $FRAMEWORK_PREFIX/..."
    git subtree pull --prefix="$FRAMEWORK_PREFIX" "$FRAMEWORK_REMOTE" "$FRAMEWORK_BRANCH" --squash -m "Update framework from upstream"

    print_success "Framework updated successfully!"
}

cmd_push() {
    check_git_repo
    check_remote

    # Check for uncommitted changes in framework directory
    if ! git diff --quiet "$FRAMEWORK_PREFIX/" 2>/dev/null; then
        print_error "You have uncommitted changes in $FRAMEWORK_PREFIX/"
        print_status "Please commit your changes first"
        exit 1
    fi

    print_status "Pushing framework changes to $FRAMEWORK_REMOTE..."
    git subtree push --prefix="$FRAMEWORK_PREFIX" "$FRAMEWORK_REMOTE" "$FRAMEWORK_BRANCH"

    print_success "Framework improvements pushed upstream!"
}

cmd_status() {
    check_git_repo

    echo ""
    print_status "Framework Sync Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if git remote get-url "$FRAMEWORK_REMOTE" > /dev/null 2>&1; then
        echo -e "Remote:    ${GREEN}$FRAMEWORK_REMOTE${NC} → $(git remote get-url $FRAMEWORK_REMOTE)"
    else
        echo -e "Remote:    ${RED}Not configured${NC}"
    fi

    echo "Prefix:    $FRAMEWORK_PREFIX/"
    echo "Branch:    $FRAMEWORK_BRANCH"

    if [ -d "$FRAMEWORK_PREFIX" ]; then
        echo -e "Directory: ${GREEN}Exists${NC}"

        # Count changes
        changed=$(git diff --name-only "$FRAMEWORK_PREFIX/" 2>/dev/null | wc -l | tr -d ' ')
        staged=$(git diff --cached --name-only "$FRAMEWORK_PREFIX/" 2>/dev/null | wc -l | tr -d ' ')

        if [ "$changed" -gt 0 ] || [ "$staged" -gt 0 ]; then
            echo -e "Changes:   ${YELLOW}$changed unstaged, $staged staged${NC}"
        else
            echo -e "Changes:   ${GREEN}Clean${NC}"
        fi
    else
        echo -e "Directory: ${RED}Not found${NC}"
    fi

    echo ""
}

cmd_init() {
    check_git_repo

    if [ -d "$FRAMEWORK_PREFIX" ]; then
        print_error "Directory $FRAMEWORK_PREFIX/ already exists"
        exit 1
    fi

    # Check if remote URL is provided
    if ! git remote get-url "$FRAMEWORK_REMOTE" > /dev/null 2>&1; then
        if [ -z "$FRAMEWORK_URL" ]; then
            print_error "Framework remote not configured"
            print_status "Either add remote first:"
            echo "    git remote add $FRAMEWORK_REMOTE <url>"
            print_status "Or set FRAMEWORK_URL environment variable:"
            echo "    FRAMEWORK_URL=https://github.com/Systemsaholic/Claude-Workspace-Framework.git ./framework-sync.sh init"
            exit 1
        fi

        print_status "Adding remote $FRAMEWORK_REMOTE..."
        git remote add "$FRAMEWORK_REMOTE" "$FRAMEWORK_URL"
    fi

    print_status "Fetching framework..."
    git fetch "$FRAMEWORK_REMOTE"

    print_status "Adding framework as subtree at $FRAMEWORK_PREFIX/..."
    git subtree add --prefix="$FRAMEWORK_PREFIX" "$FRAMEWORK_REMOTE" "$FRAMEWORK_BRANCH" --squash

    print_success "Framework initialized at $FRAMEWORK_PREFIX/"
    echo ""
    print_status "Next steps:"
    echo "  1. Create workspace directory: mkdir -p workspace/{registries,skills,memory}"
    echo "  2. Copy templates: cp $FRAMEWORK_PREFIX/templates/CLAUDE.md workspace/"
    echo "  3. Follow playbooks in $FRAMEWORK_PREFIX/playbooks/"
}

cmd_diff() {
    check_git_repo

    if [ ! -d "$FRAMEWORK_PREFIX" ]; then
        print_error "Framework directory $FRAMEWORK_PREFIX/ not found"
        exit 1
    fi

    print_status "Changes in framework directory:"
    git diff "$FRAMEWORK_PREFIX/"
}

# Main
case "${1:-help}" in
    pull)   cmd_pull ;;
    push)   cmd_push ;;
    status) cmd_status ;;
    init)   cmd_init ;;
    diff)   cmd_diff ;;
    help|--help|-h) show_help ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
