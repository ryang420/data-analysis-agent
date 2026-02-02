#!/bin/bash

set -e
# 导出环境变量：项目根目录与 Python 路径（本地运行）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
export PROJECT_ROOT="${PROJECT_ROOT:-$BACKEND_DIR}"
export PYTHONPATH="${BACKEND_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"
PORT=8000  # 避免与 macOS AirPlay(5000) 冲突

usage() {
  echo "用法: $0 -p <端口>"
}

while getopts "p:h" opt; do
  case "$opt" in
    p)
      PORT="$OPTARG"
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      echo "无效选项: -$OPTARG"
      usage
      exit 1
      ;;
  esac
done


python ${BACKEND_DIR}/src/main.py -m http -p $PORT
