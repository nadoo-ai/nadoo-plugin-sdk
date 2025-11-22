#!/bin/bash
#
# Nadoo Plugin SDK - Publish Script
# Publishes the SDK package to PyPI
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
echo -e "${BLUE}   Nadoo Plugin SDK - Publish Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Navigate to SDK root
cd "$SDK_ROOT"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}✗ Poetry is not installed${NC}"
    exit 1
fi

# Extract version from pyproject.toml
VERSION=$(grep '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo -e "${BLUE}Package version: ${GREEN}$VERSION${NC}"
echo ""

# Check if dist/ exists
if [ ! -d "dist/" ] || [ -z "$(ls -A dist/)" ]; then
    echo -e "${RED}✗ No build artifacts found in dist/${NC}"
    echo -e "${YELLOW}Run ./scripts/build.sh first${NC}"
    exit 1
fi

echo -e "${BLUE}Build artifacts:${NC}"
ls -lh dist/
echo ""

# Determine publish target
TARGET="${1:-pypi}"

if [ "$TARGET" == "test" ] || [ "$TARGET" == "testpypi" ]; then
    REPOSITORY="testpypi"
    REPOSITORY_URL="https://test.pypi.org/legacy/"
    INDEX_URL="https://test.pypi.org/simple/"
    INSTALL_NAME="nadoo-plugin-sdk"
    echo -e "${YELLOW}Publishing to: Test PyPI${NC}"
elif [ "$TARGET" == "pypi" ] || [ "$TARGET" == "prod" ]; then
    REPOSITORY="pypi"
    REPOSITORY_URL="https://upload.pypi.org/legacy/"
    INDEX_URL="https://pypi.org/simple/"
    INSTALL_NAME="nadoo-plugin-sdk"
    echo -e "${YELLOW}Publishing to: PyPI (Production)${NC}"
else
    echo -e "${RED}✗ Invalid target: $TARGET${NC}"
    echo -e "${YELLOW}Usage: ./scripts/publish.sh [test|pypi]${NC}"
    exit 1
fi
echo ""

# Confirmation prompt for production
if [ "$TARGET" == "pypi" ] || [ "$TARGET" == "prod" ]; then
    echo -e "${RED}⚠️  WARNING: You are about to publish to PRODUCTION PyPI!${NC}"
    echo -e "${YELLOW}This action cannot be undone.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}Publication cancelled${NC}"
        exit 0
    fi
    echo ""
fi

# Check PyPI credentials
echo -e "${YELLOW}Checking PyPI credentials...${NC}"

# Try to use poetry config
if poetry config $REPOSITORY.username &> /dev/null; then
    echo -e "${GREEN}✓ Using credentials from poetry config${NC}"
else
    echo -e "${YELLOW}⚠ No credentials found in poetry config${NC}"
    echo -e "${BLUE}Configure credentials with:${NC}"
    echo -e "  ${BLUE}poetry config $REPOSITORY.username YOUR_USERNAME${NC}"
    echo -e "  ${BLUE}poetry config $REPOSITORY.password YOUR_PASSWORD${NC}"
    echo ""
    echo -e "${YELLOW}Or use environment variables:${NC}"
    echo -e "  ${BLUE}export POETRY_PYPI_TOKEN_${REPOSITORY^^}=your-token${NC}"
    echo ""

    if [ -z "$POETRY_PYPI_TOKEN_PYPI" ] && [ -z "$POETRY_PYPI_TOKEN_TESTPYPI" ]; then
        echo -e "${RED}✗ No credentials available${NC}"
        exit 1
    fi
fi
echo ""

# Publish package
echo -e "${YELLOW}Publishing package...${NC}"
if [ "$REPOSITORY" == "testpypi" ]; then
    poetry publish -r testpypi
else
    poetry publish
fi

echo -e "${GREEN}✓ Package published successfully!${NC}"
echo ""

# Provide installation instructions
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Publication successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Package published:${NC}"
echo -e "  Name: ${GREEN}nadoo-plugin-sdk${NC}"
echo -e "  Version: ${GREEN}$VERSION${NC}"
echo -e "  Repository: ${GREEN}$REPOSITORY${NC}"
echo ""

if [ "$REPOSITORY" == "testpypi" ]; then
    echo -e "${YELLOW}To install from Test PyPI:${NC}"
    echo -e "  ${BLUE}pip install --index-url $INDEX_URL --extra-index-url https://pypi.org/simple $INSTALL_NAME==$VERSION${NC}"
else
    echo -e "${YELLOW}To install:${NC}"
    echo -e "  ${BLUE}pip install $INSTALL_NAME==$VERSION${NC}"
fi
echo ""

echo -e "${YELLOW}View on PyPI:${NC}"
if [ "$REPOSITORY" == "testpypi" ]; then
    echo -e "  ${BLUE}https://test.pypi.org/project/nadoo-plugin-sdk/$VERSION/${NC}"
else
    echo -e "  ${BLUE}https://pypi.org/project/nadoo-plugin-sdk/$VERSION/${NC}"
fi
echo ""
