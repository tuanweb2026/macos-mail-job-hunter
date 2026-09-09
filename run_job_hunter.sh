#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/job_hunter.py"

echo "=================================================="
echo "🎯 ĐANG CHẠY BỘ QUÉT VIỆC LÀM TỰ ĐỘNG TỪ GMAIL..."
echo "=================================================="

# Kiểm tra ứng dụng Mail có đang mở không, nếu chưa thì bật lên
if ! pgrep -x "Mail" > /dev/null; then
    echo "[*] Đang khởi động ứng dụng Mail..."
    open -a Mail
    sleep 3
fi

# Chạy Python script
python3 "$PYTHON_SCRIPT"
