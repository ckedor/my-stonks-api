#!/usr/bin/env bash
set -e
git add .
git commit --allow-empty-message -m "" || git commit -m "deploy"
git push origin main
