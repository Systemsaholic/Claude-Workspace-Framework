#!/bin/bash
# Deploy MCP Servers
# Selectively deploy MCP servers from the catalog to your workspace
#
# Usage:
#   deploy-mcp.sh list                    # List available MCPs
#   deploy-mcp.sh info <mcp-name>         # Show MCP details
#   deploy-mcp.sh install <mcp> [mcp...]  # Install MCPs to workspace
#   deploy-mcp.sh update <mcp> [mcp...]   # Update installed MCPs
#   deploy-mcp.sh remove <mcp>            # Remove an MCP

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Determine paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_DIR="$(dirname "$SCRIPT_DIR")"
CATALOG_FILE="$FRAMEWORK_DIR/mcp-catalog/index.yaml"
WORKSPACE_DIR="${WORKSPACE_DIR:-$(pwd)}"
MCP_DIR="$WORKSPACE_DIR/mcp-servers"

# MCP servers repository
MCP_REPO="${MCP_REPO:-git@github.com:Systemsaholic/mcp-servers.git}"
MCP_REPO_HTTPS="${MCP_REPO_HTTPS:-https://github.com/Systemsaholic/mcp-servers.git}"

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_yq() {
    if ! command -v yq &> /dev/null; then
        print_error "yq is required but not installed"
        echo "Install with: brew install yq (macOS) or apt install yq (Ubuntu)"
        exit 1
    fi
}

cmd_list() {
    check_yq

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Available MCP Servers${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Group by category
    for category in $(yq '.categories | keys | .[]' "$CATALOG_FILE"); do
        category_name=$(yq ".categories.$category" "$CATALOG_FILE")
        echo -e "${CYAN}$category_name:${NC}"

        yq ".servers | to_entries | .[] | select(.value.category == \"$category\") | \"  \(.key) - \(.value.description)\"" "$CATALOG_FILE"
        echo ""
    done

    # Show installed
    if [ -d "$MCP_DIR" ]; then
        echo -e "${GREEN}Installed in this workspace:${NC}"
        for dir in "$MCP_DIR"/*/; do
            if [ -d "$dir" ]; then
                basename "$dir"
            fi
        done | sed 's/^/  /'
    fi
    echo ""
}

cmd_info() {
    check_yq
    local mcp_name="$1"

    if [ -z "$mcp_name" ]; then
        print_error "Usage: deploy-mcp.sh info <mcp-name>"
        exit 1
    fi

    # Check if MCP exists in catalog
    if ! yq -e ".servers.$mcp_name" "$CATALOG_FILE" > /dev/null 2>&1; then
        print_error "MCP '$mcp_name' not found in catalog"
        exit 1
    fi

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $mcp_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    echo -e "${CYAN}Name:${NC} $(yq ".servers.$mcp_name.name" "$CATALOG_FILE")"
    echo -e "${CYAN}Description:${NC} $(yq ".servers.$mcp_name.description" "$CATALOG_FILE")"
    echo -e "${CYAN}Category:${NC} $(yq ".servers.$mcp_name.category" "$CATALOG_FILE")"
    echo ""

    echo -e "${CYAN}Requirements:${NC}"
    yq ".servers.$mcp_name.requires[]" "$CATALOG_FILE" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
    echo ""

    echo -e "${CYAN}Environment Variables:${NC}"
    yq ".servers.$mcp_name.env_vars[]" "$CATALOG_FILE" 2>/dev/null | sed 's/^/  - /' || echo "  (none)"
    echo ""

    # Check if installed
    if [ -d "$MCP_DIR/$mcp_name" ]; then
        echo -e "${GREEN}Status: Installed${NC}"
    else
        echo -e "${YELLOW}Status: Not installed${NC}"
    fi
    echo ""
}

cmd_install() {
    check_yq

    if [ $# -eq 0 ]; then
        print_error "Usage: deploy-mcp.sh install <mcp-name> [mcp-name...]"
        exit 1
    fi

    # Create mcp-servers directory if needed
    mkdir -p "$MCP_DIR"

    # Create temp directory for cloning
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    print_status "Cloning MCP repository..."
    if git clone --depth 1 "$MCP_REPO" "$TEMP_DIR/repo" 2>/dev/null; then
        print_success "Repository cloned (SSH)"
    elif git clone --depth 1 "$MCP_REPO_HTTPS" "$TEMP_DIR/repo" 2>/dev/null; then
        print_success "Repository cloned (HTTPS)"
    else
        print_error "Failed to clone MCP repository"
        exit 1
    fi

    for mcp_name in "$@"; do
        echo ""
        print_status "Installing $mcp_name..."

        # Check if MCP exists in catalog
        if ! yq -e ".servers.$mcp_name" "$CATALOG_FILE" > /dev/null 2>&1; then
            print_warning "MCP '$mcp_name' not found in catalog, skipping"
            continue
        fi

        # Get path from catalog
        mcp_path=$(yq ".servers.$mcp_name.path" "$CATALOG_FILE")

        # Check if exists in repo
        if [ ! -d "$TEMP_DIR/repo/$mcp_path" ]; then
            print_warning "MCP '$mcp_name' not found in repository at '$mcp_path', skipping"
            continue
        fi

        # Copy to workspace
        if [ -d "$MCP_DIR/$mcp_name" ]; then
            print_warning "$mcp_name already installed, use 'update' to refresh"
        else
            cp -r "$TEMP_DIR/repo/$mcp_path" "$MCP_DIR/$mcp_name"
            print_success "$mcp_name installed to $MCP_DIR/$mcp_name"

            # Show env vars needed
            echo -e "  ${CYAN}Configure these environment variables:${NC}"
            yq ".servers.$mcp_name.env_vars[]" "$CATALOG_FILE" 2>/dev/null | sed 's/^/    - /' || true
        fi
    done

    echo ""
    print_status "Next steps:"
    echo "  1. Create/update .env file with required variables"
    echo "  2. Add MCP configuration to .mcp.json"
    echo "  3. Install dependencies: cd mcp-servers/<name> && pip install -e ."
    echo ""
}

cmd_update() {
    check_yq

    if [ $# -eq 0 ]; then
        print_error "Usage: deploy-mcp.sh update <mcp-name> [mcp-name...]"
        exit 1
    fi

    # Create temp directory for cloning
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    print_status "Cloning MCP repository..."
    if git clone --depth 1 "$MCP_REPO" "$TEMP_DIR/repo" 2>/dev/null; then
        print_success "Repository cloned (SSH)"
    elif git clone --depth 1 "$MCP_REPO_HTTPS" "$TEMP_DIR/repo" 2>/dev/null; then
        print_success "Repository cloned (HTTPS)"
    else
        print_error "Failed to clone MCP repository"
        exit 1
    fi

    for mcp_name in "$@"; do
        echo ""
        print_status "Updating $mcp_name..."

        if [ ! -d "$MCP_DIR/$mcp_name" ]; then
            print_warning "$mcp_name not installed, use 'install' first"
            continue
        fi

        # Get path from catalog
        mcp_path=$(yq ".servers.$mcp_name.path" "$CATALOG_FILE")

        # Check if exists in repo
        if [ ! -d "$TEMP_DIR/repo/$mcp_path" ]; then
            print_warning "MCP '$mcp_name' not found in repository"
            continue
        fi

        # Backup .env if exists
        if [ -f "$MCP_DIR/$mcp_name/.env" ]; then
            cp "$MCP_DIR/$mcp_name/.env" "$TEMP_DIR/$mcp_name.env.backup"
        fi

        # Remove old and copy new
        rm -rf "$MCP_DIR/$mcp_name"
        cp -r "$TEMP_DIR/repo/$mcp_path" "$MCP_DIR/$mcp_name"

        # Restore .env
        if [ -f "$TEMP_DIR/$mcp_name.env.backup" ]; then
            cp "$TEMP_DIR/$mcp_name.env.backup" "$MCP_DIR/$mcp_name/.env"
        fi

        print_success "$mcp_name updated"
    done
    echo ""
}

cmd_remove() {
    local mcp_name="$1"

    if [ -z "$mcp_name" ]; then
        print_error "Usage: deploy-mcp.sh remove <mcp-name>"
        exit 1
    fi

    if [ ! -d "$MCP_DIR/$mcp_name" ]; then
        print_error "$mcp_name is not installed"
        exit 1
    fi

    print_warning "This will remove $MCP_DIR/$mcp_name"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$MCP_DIR/$mcp_name"
        print_success "$mcp_name removed"
    else
        print_status "Cancelled"
    fi
}

show_help() {
    cat << EOF
MCP Server Deployment Tool

Selectively deploy MCP servers from the catalog to your workspace.

COMMANDS:
    list                    List all available MCP servers
    info <mcp-name>         Show details about an MCP server
    install <mcp> [mcp...]  Install one or more MCP servers
    update <mcp> [mcp...]   Update installed MCP servers
    remove <mcp>            Remove an MCP server

EXAMPLES:
    # List available MCPs
    ./deploy-mcp.sh list

    # Get info about cpanel-mcp
    ./deploy-mcp.sh info cpanel-mcp

    # Install cpanel and telegram MCPs
    ./deploy-mcp.sh install cpanel-mcp telegram-mcp

    # Update an installed MCP
    ./deploy-mcp.sh update cpanel-mcp

ENVIRONMENT:
    WORKSPACE_DIR   Workspace directory (default: current directory)
    MCP_REPO        MCP repository URL (SSH)
    MCP_REPO_HTTPS  MCP repository URL (HTTPS fallback)

EOF
}

# Main
case "${1:-help}" in
    list)    cmd_list ;;
    info)    cmd_info "$2" ;;
    install) shift; cmd_install "$@" ;;
    update)  shift; cmd_update "$@" ;;
    remove)  cmd_remove "$2" ;;
    help|--help|-h) show_help ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
