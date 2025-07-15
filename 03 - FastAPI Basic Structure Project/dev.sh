#!/bin/bash

# Development script for FastAPI project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}FastAPI Development Helper${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    if ! command_exists python; then
        echo -e "${RED}Python is not installed${NC}"
        exit 1
    fi
    
    if ! command_exists pip; then
        echo -e "${RED}pip is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Dependencies OK${NC}"
}

# Install requirements
install_requirements() {
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Requirements installed${NC}"
}

# Setup database
setup_database() {
    echo -e "${YELLOW}Setting up database...${NC}"
    
    # Initialize Alembic if not already done
    if [ ! -f "alembic.ini" ]; then
        alembic init alembic
    fi
    
    # Create initial migration
    alembic revision --autogenerate -m "Initial migration"
    
    # Apply migrations
    alembic upgrade head
    
    echo -e "${GREEN}Database setup complete${NC}"
}

# Run development server
run_dev() {
    echo -e "${YELLOW}Starting development server...${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    pytest tests/ -v
    echo -e "${GREEN}Tests completed${NC}"
}

# Run with Docker
run_docker() {
    echo -e "${YELLOW}Starting with Docker...${NC}"
    docker-compose up --build
}

# Main menu
case "$1" in
    "deps")
        check_dependencies
        ;;
    "install")
        check_dependencies
        install_requirements
        ;;
    "setup")
        check_dependencies
        install_requirements
        setup_database
        ;;
    "dev")
        run_dev
        ;;
    "test")
        run_tests
        ;;
    "docker")
        run_docker
        ;;
    *)
        echo "Usage: $0 {deps|install|setup|dev|test|docker}"
        echo ""
        echo "Commands:"
        echo "  deps    - Check dependencies"
        echo "  install - Install Python requirements"
        echo "  setup   - Full setup (install + database)"
        echo "  dev     - Run development server"
        echo "  test    - Run tests"
        echo "  docker  - Run with Docker Compose"
        exit 1
        ;;
esac
