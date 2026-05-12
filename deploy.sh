#!/bin/bash
# deploy.sh — unpack a cylinder-monitor zip and push to GitHub
# Usage: ./deploy.sh <zipfile> [commit message]
# Example: ./deploy.sh cylinder-monitor.zip "fix ring buffer injection"

set -e

ZIP="${1}"
MSG="${2:-update from zip}"

if [ -z "$ZIP" ]; then
  echo "Usage: ./deploy.sh <zipfile> [commit message]"
  exit 1
fi

if [ ! -f "$ZIP" ]; then
  echo "Error: file not found: $ZIP"
  exit 1
fi

echo "Unpacking $ZIP..."
unzip -o "$ZIP" "cylinder-monitor/*" -d /tmp/deploy_staging

echo "Copying files into repo..."
cp /tmp/deploy_staging/cylinder-monitor/* .

echo "Cleaning up staging..."
rm -rf /tmp/deploy_staging

echo "Staging changes..."
git add detector.py index.html processor.js service_worker.js manifest.json

echo "Committing..."
git commit -m "$MSG"

echo "Pushing..."
git push

echo "Done."
