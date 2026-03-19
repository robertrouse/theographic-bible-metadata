#!/usr/bin/env bash
# Build the WASM package for browser use.
# Requires: rustup, wasm-pack (cargo install wasm-pack)
set -euo pipefail

echo "Building theographic-graph WASM package..."
wasm-pack build --target web --out-dir pkg --release

echo ""
echo "Build complete! Output in wasm-graph/pkg/"
echo "Usage: import init, { TheographicGraph } from './pkg/theographic_graph.js'"
