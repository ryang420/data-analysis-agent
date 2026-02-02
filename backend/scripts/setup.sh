# 初始化目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
if [ "$PROJECT_ENV" = "DEV" ]; then
    if [ ! -d "${WORKSPACE_PATH:-$BACKEND_DIR}/assets" ]; then
        mkdir -p "${WORKSPACE_PATH:-$BACKEND_DIR}/assets"
    fi
fi

# 安装Python三方包依赖
cd "$BACKEND_DIR" && pip install -r requirements.txt

# 安装系统依赖
