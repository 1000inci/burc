# burc.1000inci.com — Yayına Alma (Deploy) Adımları

Sunucu mimarisi: **kendi sunucu + nginx + Let's Encrypt** (vault./ses./transfer. ile aynı kalıp).
Flask uygulaması gunicorn ile `127.0.0.1:8050`'de çalışır, nginx reverse-proxy yapar.

## 0) Önkoşul — DNS
`burc.1000inci.com` için sunucu IP'sine **A kaydı** ekleyin (diğer alt alanlarla aynı IP).

## 1) Kodu sunucuya gönder
```bash
# Yerelden (örnek; sunucu kullanıcı/host'unu kendinize göre değiştirin):
scp -r C:/0.PythonDeneme/Burc  KULLANICI@SUNUCU:/opt/burc
# veya git ile: sunucuda 'git clone <repo> /opt/burc'
```

## 2) Sunucuda Python ortamı
```bash
cd /opt/burc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Hızlı test:
gunicorn --workers 3 --bind 127.0.0.1:8050 wsgi:app
```

## 3) Servis (systemd)
```bash
sudo cp deploy/burc.service /etc/systemd/system/burc.service
# WorkingDirectory / User / venv yolunu kontrol edin
sudo systemctl daemon-reload
sudo systemctl enable --now burc
sudo systemctl status burc
```

## 4) nginx + SSL
```bash
sudo cp deploy/burc.1000inci.com.conf /etc/nginx/sites-available/burc.1000inci.com
sudo ln -s /etc/nginx/sites-available/burc.1000inci.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d burc.1000inci.com
```

## 5) Doğrulama
- https://burc.1000inci.com açılıyor mu?
- Takvim (flatpickr), logo ve doğum haritası görünüyor mu? (statik dosyalar)
- Yükselen + Gerçek Transit hesapları çalışıyor mu?

## Güncelleme (sonraki sürümler)
```bash
cd /opt/burc && git pull   # veya scp ile dosyaları güncelle
sudo systemctl restart burc
```
