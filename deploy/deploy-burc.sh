#!/bin/bash
# burc deploy — A1 sunucusunda: GitHub'dan son sürümü çek, bağımlılıkları güncelle, servisi yenile
set -e
BRANCH="main"
cd /opt/burc
echo "[*] GitHub'dan çekiliyor ($BRANCH)..."
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
echo "[✓] $(git rev-parse --short HEAD) $(git log -1 --pretty=%s)"
/opt/burc/venv/bin/pip install -q -r requirements.txt
sudo systemctl restart burc
sleep 2
sudo systemctl is-active --quiet burc && echo "[✓] burc aktif" || { echo "[✗] başlamadı"; sudo journalctl -u burc -n 15 --no-pager; exit 1; }
curl -s -o /dev/null -w "burc.1000inci.com → HTTP %{http_code}\n" https://burc.1000inci.com/
