#!/bin/bash
#
# Nadoo Plugin SDK - Simple Build Script
# Builds the SDK package without Poetry
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Nadoo Plugin SDK - Simple Build${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Navigate to SDK root
cd "$SDK_ROOT"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Clean previous builds
echo ""
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info nadoo_plugin.egg-info
echo -e "${GREEN}✓ Cleaned${NC}"

# Install build dependencies
echo ""
echo -e "${YELLOW}Installing build dependencies...${NC}"
python3 -m pip install --upgrade build wheel setuptools
echo -e "${GREEN}✓ Build tools installed${NC}"

# Build the package
echo ""
echo -e "${YELLOW}Building package...${NC}"
python3 -m build
echo -e "${GREEN}✓ Package built${NC}"

# Show build artifacts
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Build completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Build artifacts:${NC}"
ls -lh dist/
echo ""

# Extract version
if [ -f "pyproject.toml" ]; then
    VERSION=$(grep '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo -e "${BLUE}Package version: ${GREEN}$VERSION${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. Test the built package:"
    echo -e "     ${BLUE}pip install dist/nadoo_plugin_sdk-$VERSION-py3-none-any.whl${NC}"
    echo -e ""
    echo -e "  2. Use in plugin development:"
    echo -e "     ${BLUE}nadoo-plugin create my-plugin${NC}"
fi
echo ""
