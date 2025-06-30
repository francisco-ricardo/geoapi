#!/bin/bash

# Clean Empty Files Script
# Removes empty Python files that VS Code might recreate

echo "🧹 Cleaning empty Python files..."

# Find and remove empty Python files
EMPTY_FILES=$(find /workspace -name "*.py" -size 0 2>/dev/null)

if [ -n "$EMPTY_FILES" ]; then
    echo "Found empty files:"
    echo "$EMPTY_FILES"
    
    # Remove empty files
    find /workspace -name "*.py" -size 0 -delete 2>/dev/null
    
    echo "✅ Empty files removed!"
else
    echo "✅ No empty files found!"
fi

# Clean Python cache files
echo "🧹 Cleaning Python cache files..."
find /workspace -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
find /workspace -type f -name '*.pyc' -delete 2>/dev/null
find /workspace -type f -name '*.pyo' -delete 2>/dev/null
rm -rf /workspace/.pytest_cache 2>/dev/null
rm -rf /workspace/.mypy_cache 2>/dev/null

echo "✅ Python cache cleaned!"

# Preserve important __init__.py files
echo "🔧 Ensuring important __init__.py files exist..."

# Core package __init__.py files that should exist (but can be empty)
REQUIRED_INIT_FILES=(
    "/workspace/app/__init__.py"
    "/workspace/app/core/__init__.py"
    "/workspace/app/models/__init__.py" 
    "/workspace/app/schemas/__init__.py"
    "/workspace/app/api/__init__.py"
    "/workspace/app/api/v1/__init__.py"
    "/workspace/app/services/__init__.py"
    "/workspace/tests/__init__.py"
    "/workspace/tests/fixtures/__init__.py"
    "/workspace/tests/unit/__init__.py"
    "/workspace/tests/unit/core/__init__.py"
    "/workspace/tests/unit/models/__init__.py"
    "/workspace/tests/unit/schemas/__init__.py"
    "/workspace/tests/unit/middleware/__init__.py"
)

for init_file in "${REQUIRED_INIT_FILES[@]}"; do
    if [ ! -f "$init_file" ]; then
        echo "Creating $init_file"
        touch "$init_file"
    fi
done

echo "✅ All required __init__.py files are in place!"

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "To prevent VS Code from recreating empty files:"
echo "1. ✅ VS Code settings configured (.vscode/settings.json)"
echo "2. ✅ File exclusions configured"
echo "3. ✅ .gitignore updated with patterns"
echo "4. ✅ Required __init__.py files preserved"
echo ""
echo "Run this script whenever empty files reappear:"
echo "  bash scripts/clean_empty_files.sh"
