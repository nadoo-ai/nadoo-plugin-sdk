#!/bin/bash
#
# Nadoo Plugin SDK - Build Script
# Builds the SDK package for distribution
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
echo -e "${BLUE}   Nadoo Plugin SDK - Build Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Navigate to SDK root
cd "$SDK_ROOT"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}✗ Poetry is not installed${NC}"
    echo -e "${YELLOW}Install Poetry: curl -sSL https://install.python-poetry.org | python3 -${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Poetry found: $(poetry --version)${NC}"

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Clean previous builds
echo ""
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info nadoo_plugin.egg-info
echo -e "${GREEN}✓ Cleaned${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install --no-root
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run linters (optional, can be skipped with --skip-lint)
if [[ "$1" != "--skip-lint" ]]; then
    echo ""
    echo -e "${YELLOW}Running code quality checks...${NC}"

    # Black (formatting check)
    echo -e "${BLUE}  → Checking code formatting with black...${NC}"
    poetry run black --check nadoo_plugin/ || {
        echo -e "${RED}  ✗ Code formatting issues found. Run: poetry run black nadoo_plugin/${NC}"
        exit 1
    }
    echo -e "${GREEN}  ✓ Code formatting OK${NC}"

    # isort (import sorting check)
    echo -e "${BLUE}  → Checking import sorting with isort...${NC}"
    poetry run isort --check-only nadoo_plugin/ || {
        echo -e "${RED}  ✗ Import sorting issues found. Run: poetry run isort nadoo_plugin/${NC}"
        exit 1
    }
    echo -e "${GREEN}  ✓ Import sorting OK${NC}"

    # Flake8 (linting)
    echo -e "${BLUE}  → Running linter (flake8)...${NC}"
    poetry run flake8 nadoo_plugin/ --max-line-length=120 --extend-ignore=E203,W503 || {
        echo -e "${YELLOW}  ⚠ Linting warnings found${NC}"
    }
    echo -e "${GREEN}  ✓ Linting complete${NC}"
else
    echo -e "${YELLOW}Skipping code quality checks (--skip-lint)${NC}"
fi

# Run tests
echo ""
echo -e "${YELLOW}Running tests...${NC}"
poetry run pytest tests/ -v --cov=nadoo_plugin --cov-report=term-missing || {
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
}
echo -e "${GREEN}✓ All tests passed${NC}"

# Build the package
echo ""
echo -e "${YELLOW}Building package...${NC}"
poetry build
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

# Extract version from pyproject.toml
VERSION=$(grep '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo -e "${BLUE}Package version: ${GREEN}$VERSION${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Test the built package:"
echo -e "     ${BLUE}pip install dist/nadoo_plugin_sdk-$VERSION-py3-none-any.whl${NC}"
echo -e ""
echo -e "  2. Publish to PyPI:"
echo -e "     ${BLUE}./scripts/publish.sh${NC}"
echo ""
