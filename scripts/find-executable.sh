#!/bin/bash
# Builder-Agnostic Executable Finder
# Works with both Nixpacks and Railpack builders

find_executable() {
    local cmd=$1
    local required=${2:-false}
    
    # Try standard command resolution first (works in most environments)
    if command -v "$cmd" >/dev/null 2>&1; then
        command -v "$cmd"
        return 0
    fi
    
    # Try common paths where executables might be installed
    local common_paths=(
        "/usr/local/bin"
        "/usr/bin"
        "/bin"
        "$HOME/.local/bin"
        "/opt/bin"
        "/usr/local/sbin"
        "/usr/sbin"
        "/sbin"
    )
    
    for path in "${common_paths[@]}"; do
        if [ -x "$path/$cmd" ]; then
            echo "$path/$cmd"
            return 0
        fi
    done
    
    # If required and not found, exit with error
    if [ "$required" = "true" ]; then
        echo "ERROR: Required executable '$cmd' not found in PATH or common locations" >&2
        return 1
    fi
    
    return 1
}

# Export function for use in other scripts
export -f find_executable

# If called directly, find the requested executable
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <executable> [required]"
        echo "  executable: name of the executable to find"
        echo "  required:   'true' to exit with error if not found (default: false)"
        exit 1
    fi
    
    find_executable "$@"
fi