#!/bin/bash

# UHL Auto-Commit Script
# Automated commit, push, and release workflow for UHL operations

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Change to repository root
cd "$(dirname "$0")/../.."
REPO_ROOT=$(pwd)

echo -e "${BLUE}🏒 UHL Auto-Commit Workflow${NC}"
echo "=================================="
echo "Repository: $(basename "$REPO_ROOT")"
echo "Current branch: $(git branch --show-current)"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

# Check for uncommitted changes
if git diff-index --quiet HEAD --; then
    print_warning "No changes to commit"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 0
    fi
fi

# Show current status
print_info "Current git status:"
git status --short
echo ""

# Determine commit type and message
COMMIT_TYPE=""
COMMIT_MSG=""
VERSION_TYPE="patch"

# Check if this looks like a gameday update
if [ -f "ops/output/schedule.json" ] && [ -f "ops/output/players.json" ] && [ -f "ops/output/goalie_stats.json" ]; then
    COMMIT_TYPE="gameday"
    
    # Get game data for commit message
    GAMES_COUNT=$(cat ops/output/schedule.json | grep -o '"id"' | wc -l | tr -d ' ')
    PLAYERS_COUNT=$(cat ops/output/players.json | grep -o '"firstName"' | wc -l | tr -d ' ')
    GOALIES_COUNT=$(cat ops/output/goalie_stats.json | grep -o '"firstName"' | wc -l | tr -d ' ')
    
    COMMIT_MSG="gameday: Update UHL data - ${GAMES_COUNT} games, ${PLAYERS_COUNT} players, ${GOALIES_COUNT} goalies"
    
elif [ -d "ops/scripts" ] && [ -f "ops/scripts/weekly_update.sh" ]; then
    COMMIT_TYPE="ops"
    COMMIT_MSG="ops: Improve UHL operations system"
    VERSION_TYPE="minor"
    
else
    COMMIT_TYPE="feat"
    COMMIT_MSG="feat: Update hockey league system"
fi

# Allow user to customize commit message
echo -e "${YELLOW}Suggested commit message:${NC}"
echo "  $COMMIT_MSG"
echo ""
read -p "Use this message? (Y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Enter your commit message:"
    read -r CUSTOM_MSG
    if [ -n "$CUSTOM_MSG" ]; then
        COMMIT_MSG="$CUSTOM_MSG"
    fi
fi

# Ask about version bump for release
echo ""
echo -e "${YELLOW}Release version bump:${NC}"
echo "1) patch (1.0.1 -> 1.0.2) - Bug fixes, data updates"
echo "2) minor (1.0.1 -> 1.1.0) - New features, improvements"  
echo "3) major (1.0.1 -> 2.0.0) - Breaking changes"
echo "4) skip - No release, just commit and push"
echo ""
read -p "Select version bump (1-4) [default: 1]: " -n 1 -r
echo

case $REPLY in
    2) VERSION_TYPE="minor" ;;
    3) VERSION_TYPE="major" ;;
    4) VERSION_TYPE="skip" ;;
    *) VERSION_TYPE="patch" ;;
esac

# Stage all changes
print_info "Staging changes..."
git add .
print_status "Changes staged"

# Commit changes
print_info "Committing changes..."
if git commit -m "$COMMIT_MSG"; then
    print_status "Changes committed"
else
    print_error "Commit failed!"
    exit 1
fi

# Push changes
print_info "Pushing to origin..."
if git push; then
    print_status "Changes pushed to remote"
else
    print_error "Push failed!"
    exit 1
fi

# Create release if requested
if [ "$VERSION_TYPE" != "skip" ]; then
    echo ""
    print_info "Creating release..."
    
    # Get current version from existing tags
    CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    
    # Remove 'v' prefix if present
    CURRENT_VERSION=${CURRENT_TAG#v}
    
    # Parse version parts
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR=${VERSION_PARTS[0]:-0}
    MINOR=${VERSION_PARTS[1]:-0}
    PATCH=${VERSION_PARTS[2]:-0}
    
    # Bump version based on type
    case $VERSION_TYPE in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        patch)
            PATCH=$((PATCH + 1))
            ;;
    esac
    
    NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"
    
    # Create release notes
    RELEASE_NOTES=""
    if [ "$COMMIT_TYPE" = "gameday" ]; then
        RELEASE_NOTES="🏒 Gameday Update ${NEW_VERSION}

## Data Updates
- Updated schedule with ${GAMES_COUNT} games
- Processed ${PLAYERS_COUNT} player records  
- Calculated statistics for ${GOALIES_COUNT} goalies

## Files Updated
- \`schedule.json\` - Complete game schedule with lineups
- \`players.json\` - Player data and season statistics
- \`standings.json\` - Team standings and records
- \`goalie_stats.json\` - Goalie performance metrics

Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    elif [ "$COMMIT_TYPE" = "ops" ]; then
        RELEASE_NOTES="🔧 Operations Update ${NEW_VERSION}

## System Improvements
- Enhanced UHL operations workflow
- Improved automation scripts
- Better error handling and logging

## Technical Updates
- Streamlined data processing
- Updated configuration management
- Enhanced reliability and performance

Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    else
        RELEASE_NOTES="🚀 UHL System Update ${NEW_VERSION}

## Updates
${COMMIT_MSG}

Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # Create and push tag
    if git tag -a "$NEW_VERSION" -m "$RELEASE_NOTES"; then
        print_status "Tag $NEW_VERSION created"
        
        if git push origin "$NEW_VERSION"; then
            print_status "Tag pushed to remote"
            
            # Create GitHub release (if gh CLI is available)
            if command -v gh >/dev/null 2>&1; then
                print_info "Creating GitHub release..."
                if gh release create "$NEW_VERSION" --title "$NEW_VERSION" --notes "$RELEASE_NOTES"; then
                    print_status "GitHub release created: $NEW_VERSION"
                else
                    print_warning "GitHub release creation failed (tag still created)"
                fi
            else
                print_warning "GitHub CLI not available - tag created but no release"
                print_info "Install 'gh' CLI to enable automatic GitHub releases"
            fi
        else
            print_error "Failed to push tag"
        fi
    else
        print_error "Failed to create tag"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Auto-commit workflow complete!${NC}"
echo "=================================="
print_status "Commit: $COMMIT_MSG"
print_status "Pushed to: $(git branch --show-current)"
if [ "$VERSION_TYPE" != "skip" ]; then
    print_status "Release: $NEW_VERSION"
fi
echo ""
print_info "Repository: https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/' | sed 's/\.git$//')"
