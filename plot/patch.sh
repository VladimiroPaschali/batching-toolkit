#!/bin/bash


# this script applies a patch to the textual-plotex library wich do not support annotations


help() {
    echo "Usage: $0 <path to textual-plotex> [options]"
    echo "patch.sh .venv/lib/python3.11/site-packages/textual_plotext"
    echo "Options:"
    echo "  -h, --help     Show this help message"
}


if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    help
    exit 0
fi

if [[ -z "$1" ]]; then
    echo "Error: No path to textual-plotex provided."
    help
    exit 1
fi

PATCH_DIR=$(dirname "$1")

# check if textual-plotex exists
if [[ ! -d "$PATCH_DIR" ]]; then
    echo "Error: The specified path '$PATCH_DIR' does not exist."
    exit 1
fi



# do backup
echo "Creating backup of plotext_plot.py in $PATCH_DIR/plotext_plot.py.bak"
cp -v "$PATCH_DIR/plotext_plot.py" "$PATCH_DIR/plotext_plot.py.bak"

echo "Applying patch to textual-plotex in $PATCH_DIR"

cp -v "plotext_patched.py" "$PATCH_DIR/plotext_plot.py"

if [[ $? -ne 0 ]]; then
    echo "Error: Failed to apply patch."
    exit 1
fi

echo "Patch applied successfully. You can now use annotations in textual-plotex."