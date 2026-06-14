#!/bin/bash

# Setup colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Agents Skills Installer ===${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git first.${NC}"
    exit 1
fi

PLUGIN_DIR="$HOME/.gemini/config/plugins"
TARGET_DIR="$PLUGIN_DIR/Agents-skills"

# Create the plugins directory if it doesn't exist
mkdir -p "$PLUGIN_DIR"

if [ -d "$TARGET_DIR" ]; then
    echo -e "${BLUE}Existing installation found. Updating...${NC}"
    cd "$TARGET_DIR" || exit 1
    if git pull; then
        echo -e "${GREEN}Successfully updated AI Agents Skills!${NC}"
    else
        echo -e "${RED}Failed to update repository. Please check your network connection.${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}Cloning AI Agents Skills repository into $TARGET_DIR...${NC}"
    if git clone https://github.com/satiricalguru/Agents-skills.git "$TARGET_DIR"; then
        echo -e "${GREEN}Successfully installed AI Agents Skills!${NC}"
    else
        echo -e "${RED}Failed to clone repository. Please check your network connection.${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}Installation complete! Please restart your IDE/Agent to load the skills.${NC}"
