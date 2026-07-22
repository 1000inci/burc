# -*- coding: utf-8 -*-
"""
app.py — Burç Uygulaması web sunucusu (Flask).
Mevcut modülleri (burc, astro, uyum, yorum) JSON API olarak sunar
ve tek sayfalık arayüzü (templates/index.html) gösterir.

Çalıştırma:
    python app.py
    Tarayıcı: http://127.0.0.1:5000
"""

from datetime import datetime, date
from functools import lru_cache
from flask import Flask, render_template, request, jsonify

import burc as burc_mod
import uyum as uyum_mod
import yorum as yorum_mod

try:
    import astro
    import transit as transit_mod
    ASTRO_VAR = True
except ImportError:
    ASTRO_VAR = False

app = Flask(__name__)


# --- Basit önbellek: harita/transit hesapları girdiye göre deterministiktir.
# Aynı doğum verisi + gün için Swiss Ephemeris'i tekrar çalıştırmayalım.
# Not: Çağıranlar dönen sözlüğe üst düzey anahtar eklerken önce sığ kopya alır.
@lru_cache(maxsize=512)
def _harita_cached(yil, ay, gun, saat, dakika, enlem, boylam, utc):
    return astro.harita_detay(yil, ay, gun, saat, dakika, enlem, boylam, utc)


@lru_cache(maxsize=512)
def _transit_cached(yil, ay, gun, saat, dakika, enlem, boylam, utc, hedef_iso):
    hedef = date.fromisoformat(hedef_iso) if hedef_iso else None
    return transit_mod.gunluk_transit(
        yil, ay, gun, saat, dakika, enlem, boylam, utc, hedef)


def _utc_elle(request):
    """Kullanıcı UTC'yi elle mi girdi? (boş / 'auto' değilse evet)"""
    ham = (request.args.get("utc") or "").strip().lower()
    return ham not in ("", "auto", "oto", "otomatik")


def _coz_utc(request, t, saat, dakika, sehir):
    """UTC farkını çözer: elle girildiyse onu, yoksa tarihe göre otomatik."""
    ham = (request.args.get("utc") or "").strip().lower()
    if _utc_elle(request):
        try:
            return float(ham.replace(",", "."))
        except ValueError:
            pass
    # Otomatik: şehrin saat dilimine göre o tarihteki gerçek fark
    tz = astro.sehir_tz(sehir) if ASTRO_VAR else "Europe/Istanbul"
    return astro.otomatik_utc(t.year, t.month, t.day, saat, dakika, tz)


def _burc_sozluk(b):
    ad, (ay, gun), element, gezegen, ozellik = b
    return {"ad": ad, "element": element, "gezegen": gezegen, "ozellik": ozellik}


def _konum_coz(request):
    """İstekten (enlem, boylam, sehir) çözer; çözülemezse None döndürür."""
    sehir = request.args.get("sehir", "").lower()
    if sehir in astro.SEHIRLER:
        enlem, boylam = astro.SEHIRLER[sehir]
        return enlem, boylam, sehir
    try:
        return float(request.args["enlem"]), float(request.args["boylam"]), sehir
    except (KeyError, ValueError):
        return None


def _gunluk_transit_vurgu(request):
    """
    Yorum sekmesi için: doğum bilgisi verildiyse BUGÜNÜN en belirgin gerçek
    transitini döndürür. Bilgi eksik ya da astro yoksa None.
    """
    if not ASTRO_VAR:
        return None
    try:
        t = datetime.strptime(request.args["tarih"], "%Y-%m-%d")
        saat, dakika = (int(x) for x in request.args["saat"].split(":"))
    except (KeyError, ValueError):
        return None
    konum = _konum_coz(request)
    if not konum:
        return None
    enlem, boylam, sehir = konum
    utc = _coz_utc(request, t, saat, dakika, sehir)
    sonuc = _transit_cached(
        t.year, t.month, t.day, saat, dakika, enlem, boylam, round(utc, 4), None)
    yorumlar = sonuc.get("yorumlar") or []
    return yorumlar[0] if yorumlar else None


@app.route("/")
def index():
    return render_template(
        "index.html",
        burclar=[b[0] for b in burc_mod.BURCLAR],
        sehirler=sorted(astro.SEHIRLER.keys()) if ASTRO_VAR else [],
        astro_var=ASTRO_VAR,
    )


@app.route("/api/burc")
def api_burc():
    """Doğum tarihinden güneş burcu."""
    try:
        t = datetime.strptime(request.args["tarih"], "%Y-%m-%d")
    except (KeyError, ValueError):
        return jsonify({"hata": "Geçerli tarih girin (YYYY-AA-GG)."}), 400
    return jsonify(_burc_sozluk(burc_mod.burc_bul(t.month, t.day)))


@app.route("/api/yukselen")
def api_yukselen():
    """Gerçek yükselen + doğum haritası (Swiss Ephemeris)."""
    if not ASTRO_VAR:
        return jsonify({"hata": "pyswisseph kurulu değil."}), 503
    try:
        t = datetime.strptime(request.args["tarih"], "%Y-%m-%d")
        saat, dakika = (int(x) for x in request.args["saat"].split(":"))
    except (KeyError, ValueError):
        return jsonify({"hata": "Tarih/saat hatalı."}), 400

    sehir = request.args.get("sehir", "").lower()
    if sehir in astro.SEHIRLER:
        enlem, boylam = astro.SEHIRLER[sehir]
    else:
        try:
            enlem = float(request.args["enlem"])
            boylam = float(request.args["boylam"])
        except (KeyError, ValueError):
            return jsonify({"hata": "Şehir ya da enlem/boylam gerekli."}), 400

    utc = _coz_utc(request, t, saat, dakika, sehir)

    detay = dict(_harita_cached(
        t.year, t.month, t.day, saat, dakika, enlem, boylam, round(utc, 4)))
    detay["gunes"] = _burc_sozluk(burc_mod.burc_bul(t.month, t.day))
    detay["utc_kullanilan"] = round(utc, 1)
    detay["utc_otomatik"] = not _utc_elle(request)
    return jsonify(detay)


@app.route("/api/transit")
def api_transit():
    """Doğum verisi + bugünden GERÇEK transit yorumu."""
    if not ASTRO_VAR:
        return jsonify({"hata": "pyswisseph kurulu değil."}), 503
    try:
        t = datetime.strptime(request.args["tarih"], "%Y-%m-%d")
        saat, dakika = (int(x) for x in request.args["saat"].split(":"))
    except (KeyError, ValueError):
        return jsonify({"hata": "Tarih/saat hatalı."}), 400

    sehir = request.args.get("sehir", "").lower()
    if sehir in astro.SEHIRLER:
        enlem, boylam = astro.SEHIRLER[sehir]
    else:
        try:
            enlem = float(request.args["enlem"])
            boylam = float(request.args["boylam"])
        except (KeyError, ValueError):
            return jsonify({"hata": "Şehir ya da enlem/boylam gerekli."}), 400

    hedef = None
    if request.args.get("gun"):
        try:
            hedef = datetime.strptime(request.args["gun"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"hata": "Hedef gün hatalı."}), 400

    utc = _coz_utc(request, t, saat, dakika, sehir)
    hedef_iso = hedef.isoformat() if hedef else None
    sonuc = dict(_transit_cached(
        t.year, t.month, t.day, saat, dakika, enlem, boylam,
        round(utc, 4), hedef_iso))
    sonuc["utc_kullanilan"] = round(utc, 1)
    sonuc["utc_otomatik"] = not _utc_elle(request)
    return jsonify(sonuc)


@app.route("/api/uyum")
def api_uyum():
    b1 = request.args.get("b1", "")
    b2 = request.args.get("b2", "")
    gecerli = {b[0] for b in burc_mod.BURCLAR}
    if b1 not in gecerli or b2 not in gecerli:
        return jsonify({"hata": "Geçerli iki burç seçin."}), 400
    aci, puan, yorum, el = uyum_mod.uyum(b1, b2)
    return jsonify({"b1": b1, "b2": b2, "aci": aci, "puan": puan,
                    "yorum": yorum, "element": el})


@app.route("/api/uyum/matris")
def api_uyum_matris():
    siralar = uyum_mod.BURC_SIRA
    matris = [[uyum_mod.uyum(a, b)[1] for b in siralar] for a in siralar]
    return jsonify({"burclar": siralar, "matris": matris})


@app.route("/api/yorum")
def api_yorum():
    burc = request.args.get("burc", "")
    if burc not in {b[0] for b in burc_mod.BURCLAR}:
        return jsonify({"hata": "Geçerli bir burç seçin."}), 400
    if request.args.get("tip") == "haftalik":
        from datetime import date, timedelta
        bugun = date.today()
        bas = bugun - timedelta(days=bugun.weekday())
        gunler = []
        for i in range(7):
            g = bas + timedelta(days=i)
            gunler.append(yorum_mod.gunluk_yorum(burc, g))
        return jsonify({"tip": "haftalik", "gunler": gunler})
    sonuc = {"tip": "gunluk", **yorum_mod.gunluk_yorum(burc)}
    vurgu = _gunluk_transit_vurgu(request)
    if vurgu:
        sonuc["gercek_transit"] = vurgu
    return jsonify(sonuc)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
