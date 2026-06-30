# -*- coding: utf-8 -*-
"""
wsgi.py — Üretim (production) giriş noktası.
gunicorn bu dosyadaki 'app' nesnesini çalıştırır:

    gunicorn --workers 3 --bind 127.0.0.1:8050 wsgi:app

Yerel geliştirme için yine 'python app.py' kullanılabilir.
"""

from app import app

if __name__ == "__main__":
    app.run()
