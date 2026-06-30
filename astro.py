# -*- coding: utf-8 -*-
"""
astro.py — Swiss Ephemeris (pyswisseph) ile gerçek astrolojik hesaplar.
- Yükselen burç (Ascendant)
- Gezegen konumları (Güneş, Ay ve gezegenler)
Tropikal zodyak, Placidus ev sistemi.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import swisseph as swe

# Şehir -> IANA saat dilimi. Türkiye'nin tamamı Europe/Istanbul;
# KKTC (Lefkoşa, Girne) Asia/Nicosia. zoneinfo geçmiş yaz saati /
# standart saat geçişlerini otomatik bilir.
VARSAYILAN_TZ = "Europe/Istanbul"
SEHIR_TZ = {"lefkosa": "Asia/Nicosia", "girne": "Asia/Nicosia"}


def sehir_tz(sehir):
    return SEHIR_TZ.get((sehir or "").lower(), VARSAYILAN_TZ)


def otomatik_utc(yil, ay, gun, saat, dakika, tz_ad=VARSAYILAN_TZ):
    """
    Verilen yerel doğum zamanı için o tarihte geçerli UTC farkını (saat)
    otomatik döndürür. Yaz saati / standart saat geçişlerini dikkate alır.
    """
    dt = datetime(yil, ay, gun, saat, dakika, tzinfo=ZoneInfo(tz_ad))
    return dt.utcoffset().total_seconds() / 3600.0

# Tropikal zodyak: 0° = Koç başlangıcı
BURC_TROPIK = [
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık",
]

# Türkiye'nin 81 ili + KKTC: (enlem, boylam)  +K / +D pozitif
SEHIRLER = {
    "adana": (37.0000, 35.3213), "adiyaman": (37.7648, 38.2786),
    "afyonkarahisar": (38.7507, 30.5567), "agri": (39.7191, 43.0503),
    "aksaray": (38.3687, 34.0370), "amasya": (40.6499, 35.8353),
    "ankara": (39.9334, 32.8597), "antalya": (36.8969, 30.7133),
    "ardahan": (41.1105, 42.7022), "artvin": (41.1828, 41.8183),
    "aydin": (37.8560, 27.8416), "balikesir": (39.6484, 27.8826),
    "bartin": (41.6344, 32.3375), "batman": (37.8812, 41.1351),
    "bayburt": (40.2552, 40.2249), "bilecik": (40.0567, 30.0665),
    "bingol": (38.8855, 40.4966), "bitlis": (38.4006, 42.1095),
    "bolu": (40.7392, 31.6089), "burdur": (37.7203, 30.2908),
    "bursa": (40.1828, 29.0665), "canakkale": (40.1553, 26.4142),
    "cankiri": (40.6013, 33.6134), "corum": (40.5506, 34.9556),
    "denizli": (37.7765, 29.0864), "diyarbakir": (37.9144, 40.2306),
    "duzce": (40.8438, 31.1565), "edirne": (41.6818, 26.5623),
    "elazig": (38.6810, 39.2264), "erzincan": (39.7500, 39.5000),
    "erzurum": (39.9000, 41.2700), "eskisehir": (39.7767, 30.5206),
    "gaziantep": (37.0662, 37.3833), "giresun": (40.9128, 38.3895),
    "gumushane": (40.4603, 39.4814), "hakkari": (37.5744, 43.7408),
    "hatay": (36.4018, 36.3498), "igdir": (39.8880, 44.0048),
    "isparta": (37.7648, 30.5566), "istanbul": (41.0082, 28.9784),
    "izmir": (38.4237, 27.1428), "kahramanmaras": (37.5858, 36.9371),
    "karabuk": (41.2061, 32.6204), "karaman": (37.1759, 33.2287),
    "kars": (40.6013, 43.0975), "kastamonu": (41.3887, 33.7827),
    "kayseri": (38.7312, 35.4787), "kilis": (36.7184, 37.1212),
    "kirikkale": (39.8468, 33.5153), "kirklareli": (41.7333, 27.2167),
    "kirsehir": (39.1425, 34.1709), "kocaeli": (40.8533, 29.8815),
    "konya": (37.8746, 32.4932), "kutahya": (39.4242, 29.9833),
    "malatya": (38.3552, 38.3095), "manisa": (38.6191, 27.4289),
    "mardin": (37.3212, 40.7245), "mersin": (36.8121, 34.6415),
    "mugla": (37.2153, 28.3636), "mus": (38.7432, 41.5064),
    "nevsehir": (38.6939, 34.6857), "nigde": (37.9667, 34.6833),
    "ordu": (40.9839, 37.8764), "osmaniye": (37.2130, 36.1763),
    "rize": (41.0201, 40.5234), "sakarya": (40.7569, 30.3783),
    "samsun": (41.2867, 36.3300), "sanliurfa": (37.1591, 38.7969),
    "siirt": (37.9333, 41.9500), "sinop": (42.0231, 35.1531),
    "sivas": (39.7477, 37.0179), "sirnak": (37.5164, 42.4611),
    "tekirdag": (40.9833, 27.5167), "tokat": (40.3167, 36.5544),
    "trabzon": (41.0015, 39.7178), "tunceli": (39.1079, 39.5401),
    "usak": (38.6823, 29.4082), "van": (38.4891, 43.4089),
    "yalova": (40.6500, 29.2667), "yozgat": (39.8181, 34.8147),
    "zonguldak": (41.4564, 31.7987),
    "lefkosa": (35.1856, 33.3823), "girne": (35.3417, 33.3192),  # KKTC
}

GEZEGENLER = [
    ("Güneş",   swe.SUN),
    ("Ay",      swe.MOON),
    ("Merkür",  swe.MERCURY),
    ("Venüs",   swe.VENUS),
    ("Mars",    swe.MARS),
    ("Jüpiter", swe.JUPITER),
    ("Satürn",  swe.SATURN),
    ("Uranüs",  swe.URANUS),
    ("Neptün",  swe.NEPTUNE),
    ("Plüton",  swe.PLUTO),
]


def _burc_ve_derece(boylam):
    """Ekliptik boylamdan (0-360) burç adı ve burç içi dereceyi döndürür."""
    boylam = boylam % 360.0
    index = int(boylam // 30) % 12
    derece = boylam % 30
    return BURC_TROPIK[index], derece


def _julian_day(yil, ay, gun, saat, dakika, utc_offset):
    """Yerel doğum zamanını UT Julian Day'e çevirir."""
    saat_ut = saat + dakika / 60.0 - utc_offset
    return swe.julday(yil, ay, gun, saat_ut, swe.GREG_CAL)


def yukselen_hesapla(yil, ay, gun, saat, dakika, enlem, boylam, utc_offset=3.0):
    """
    Gerçek yükselen burç (Ascendant) hesabı.
    Döner: (burç_adı, burç_içi_derece, tam_boylam)
    """
    jd = _julian_day(yil, ay, gun, saat, dakika, utc_offset)
    # Placidus ev sistemi; ascmc[0] = Ascendant boylamı
    _cusps, ascmc = swe.houses(jd, enlem, boylam, b'P')
    asc_boylam = ascmc[0]
    ad, derece = _burc_ve_derece(asc_boylam)
    return ad, derece, asc_boylam


def gezegen_konumlari(yil, ay, gun, saat, dakika, utc_offset=3.0):
    """
    Doğum anındaki gezegen konumları.
    Döner: [(gezegen_adı, burç_adı, burç_içi_derece), ...]
    """
    jd = _julian_day(yil, ay, gun, saat, dakika, utc_offset)
    sonuc = []
    for ad, pid in GEZEGENLER:
        konum, _ret = swe.calc_ut(jd, pid)
        boylam = konum[0]
        burc, derece = _burc_ve_derece(boylam)
        sonuc.append((ad, burc, derece))
    return sonuc


def harita_detay(yil, ay, gun, saat, dakika, enlem, boylam, utc_offset=3.0):
    """
    Web çarkı için ayrıntılı veri: mutlak ekliptik boylamlar dahil.
    Döner: {"yukselen": {...}, "gezegenler": [ {...}, ... ]}
    """
    jd = _julian_day(yil, ay, gun, saat, dakika, utc_offset)
    _cusps, ascmc = swe.houses(jd, enlem, boylam, b'P')
    asc_boylam = ascmc[0]
    asc_ad, asc_derece = _burc_ve_derece(asc_boylam)

    gezegenler = []
    for ad, pid in GEZEGENLER:
        konum, _ = swe.calc_ut(jd, pid)
        boy = konum[0]
        burc, derece = _burc_ve_derece(boy)
        gezegenler.append({
            "ad": ad, "burc": burc, "derece": round(derece, 2),
            "boylam": round(boy % 360, 2),
        })
    return {
        "yukselen": {"burc": asc_ad, "derece": round(asc_derece, 2),
                     "boylam": round(asc_boylam % 360, 2)},
        "gezegenler": gezegenler,
    }


def harita_ozeti(yil, ay, gun, saat, dakika, enlem, boylam, utc_offset=3.0):
    """Yükselen + gezegenleri tek seferde hesaplar (sözlük döner)."""
    yuk_ad, yuk_derece, _ = yukselen_hesapla(
        yil, ay, gun, saat, dakika, enlem, boylam, utc_offset
    )
    return {
        "yukselen": (yuk_ad, yuk_derece),
        "gezegenler": gezegen_konumlari(yil, ay, gun, saat, dakika, utc_offset),
    }


if __name__ == "__main__":
    # Hızlı kendi kendine test: 25.04.1990 14:30, İstanbul, UTC+3
    enlem, boylam = SEHIRLER["istanbul"]
    h = harita_ozeti(1990, 4, 25, 14, 30, enlem, boylam, 3.0)
    ya, yd = h["yukselen"]
    print(f"Yükselen: {ya} {yd:.1f}°")
    for ad, burc, derece in h["gezegenler"]:
        print(f"  {ad:8s}: {burc:8s} {derece:5.1f}°")
