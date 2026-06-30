# DEVİR NOTU — burc.1000inci.com yayına alma (sunucu yöneten oturuma)

Bu uygulama yayına alınmaya hazır. Sunucu mimarisi mevcut alt alanlarla **aynı**:
kendi sunucu + nginx reverse-proxy + Let's Encrypt (vault./ses./transfer. gibi).

## Uygulama özeti
- **Ne**: Flask tabanlı "Burç Uygulaması" (güneş burcu, yükselen + doğum haritası,
  gerçek transit, burç uyumu, günlük/haftalık yorum).
- **Yerel konum**: `C:\0.PythonDeneme\Burc`
- **Çalışma**: gunicorn ile `127.0.0.1:8050`, nginx önünde proxy.
- **Statik**: `static/` içinde flatpickr (çevrimdışı takvim) + `macar-logo.png`.
- **Bağımlılıklar**: `requirements.txt` (flask, pyswisseph, tzdata, gunicorn).
  - pyswisseph Linux'ta pip wheel ile sorunsuz kurulur.
  - tzdata, yükselen hesabında geçmiş saat dilimi (yaz/kış) doğruluğu için gerekli.

## Hedef
- Alt alan: **burc.1000inci.com**
- DNS: `burc.1000inci.com` → sunucu IP (A kaydı) — diğer alt alanlarla aynı IP.

## Hazır deploy dosyaları (deploy/ klasöründe)
- `burc.service` — systemd servisi (gunicorn, otomatik yeniden başlatma)
- `burc.1000inci.com.conf` — nginx server block (proxy + /static/ doğrudan servis)
- `DEPLOY.md` — adım adım komutlar
- `.gitignore` — server.log / __pycache__ / venv hariç

## Yapılacaklar (özet)
1. DNS A kaydı: burc.1000inci.com → IP
2. Kodu sunucuya al: `/opt/burc` (scp ya da git clone)
3. venv + `pip install -r requirements.txt`
4. `deploy/burc.service` → systemd, `enable --now`
5. `deploy/burc.1000inci.com.conf` → nginx sites-enabled, `nginx -t && reload`
6. `certbot --nginx -d burc.1000inci.com`
7. Doğrula: https://burc.1000inci.com (takvim, logo, harita, transit çalışıyor mu?)

Detaylı komutlar için: `deploy/DEPLOY.md`
