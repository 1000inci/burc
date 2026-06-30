# -*- coding: utf-8 -*-
"""
Burç Uygulaması
- Doğum tarihinden burç tespiti
- Burçlar hakkında bilgi
- (İsteyene) doğum saati + tarihinden yaklaşık yükselen burç hesabı
"""

from datetime import datetime

try:
    import astro
    ASTRO_VAR = True
except ImportError:
    ASTRO_VAR = False

try:
    import uyum as uyum_mod
    import yorum as yorum_mod
    EK_VAR = True
except ImportError:
    EK_VAR = False

# --- Burç verileri -----------------------------------------------------------
# (ad, başlangıç (ay, gün), element, yönetici gezegen, kısa özellik)
BURCLAR = [
    ("Oğlak",   (12, 22), "Toprak", "Satürn",  "Disiplinli, sabırlı, hırslı ve sorumluluk sahibi."),
    ("Kova",    (1, 20),  "Hava",   "Uranüs",  "Özgürlükçü, yenilikçi, bağımsız ve insancıl."),
    ("Balık",   (2, 19),  "Su",     "Neptün",  "Hayalperest, duygusal, sezgisel ve şefkatli."),
    ("Koç",     (3, 21),  "Ateş",   "Mars",    "Cesur, enerjik, öncü ve girişken."),
    ("Boğa",    (4, 20),  "Toprak", "Venüs",   "Kararlı, güvenilir, sabırlı ve konforu seven."),
    ("İkizler", (5, 21),  "Hava",   "Merkür",  "Meraklı, zeki, iletişimci ve uyumlu."),
    ("Yengeç",  (6, 22),  "Su",     "Ay",      "Duygusal, koruyucu, sadık ve aile odaklı."),
    ("Aslan",   (7, 23),  "Ateş",   "Güneş",   "Kendine güvenen, cömert, lider ruhlu ve gururlu."),
    ("Başak",   (8, 23),  "Toprak", "Merkür",  "Titiz, analitik, çalışkan ve mükemmeliyetçi."),
    ("Terazi",  (9, 23),  "Hava",   "Venüs",   "Dengeli, adil, zarif ve uyumu seven."),
    ("Akrep",   (10, 23), "Su",     "Plüton",  "Tutkulu, kararlı, gizemli ve derin."),
    ("Yay",     (11, 22), "Ateş",   "Jüpiter", "Özgür, iyimser, maceracı ve felsefi."),
]


def burc_bul(ay, gun):
    """Verilen ay/gün için burcu döndürür."""
    # Oğlak yıl sonundan başlar; tarihleri sırayla kontrol et
    for i in range(len(BURCLAR)):
        ad, (b_ay, b_gun), *_ = BURCLAR[i]
        sonraki = BURCLAR[(i + 1) % len(BURCLAR)]
        s_ay, s_gun = sonraki[1]
        if i == 0:  # Oğlak: 22 Aralık - 19 Ocak
            if (ay == 12 and gun >= 22) or (ay == 1 and gun <= 19):
                return BURCLAR[i]
        else:
            if (ay == b_ay and gun >= b_gun) or (ay == s_ay and gun < s_gun):
                return BURCLAR[i]
    return BURCLAR[0]


def yukselen_burc(ay, gun, saat, dakika):
    """
    Yaklaşık yükselen burç hesabı.
    Basitleştirilmiş yöntem: Güneş burcundan başlayıp doğum saatine göre
    her ~2 saatte bir burç ilerletir. Kesin sonuç için doğum yeri/enlemi
    ve sideral zaman gerekir; bu bir tahmindir.
    """
    gunes = burc_bul(ay, gun)
    gunes_index = BURCLAR.index(gunes)

    # Gün doğumunu (yaklaşık 06:00) referans alıp her 2 saate 1 burç ekle
    toplam_dakika = saat * 60 + dakika
    referans = 6 * 60  # 06:00
    fark_dakika = (toplam_dakika - referans) % (24 * 60)
    adim = fark_dakika // 120  # her 120 dakikada bir burç

    yuk_index = (gunes_index + adim) % len(BURCLAR)
    return BURCLAR[yuk_index]


def burc_yazdir(burc, baslik="Burcunuz"):
    ad, (ay, gun), element, gezegen, ozellik = burc
    print(f"\n  {baslik}: {ad}")
    print(f"  Element        : {element}")
    print(f"  Yönetici Gezegen: {gezegen}")
    print(f"  Özellikler     : {ozellik}\n")


def tum_burclari_listele():
    print("\n=== Tüm Burçlar ===\n")
    sirali = sorted(BURCLAR, key=lambda b: (b[1][0], b[1][1]))
    for ad, (ay, gun), element, gezegen, ozellik in BURCLAR:
        print(f"  {ad:8s} | {element:6s} | {gezegen:8s} | {ozellik}")
    print()


def tarih_al():
    while True:
        try:
            ham = input("  Doğum tarihiniz (GG.AA.YYYY): ").strip()
            t = datetime.strptime(ham, "%d.%m.%Y")
            return t.day, t.month, t.year
        except ValueError:
            print("  ! Hatalı format. Örnek: 25.04.1990")


def saat_al():
    while True:
        try:
            ham = input("  Doğum saatiniz (SS:DD, örn 14:30): ").strip()
            t = datetime.strptime(ham, "%H:%M")
            return t.hour, t.minute
        except ValueError:
            print("  ! Hatalı format. Örnek: 09:15")


def sehir_al():
    """Şehir adı veya elle enlem/boylam alır. (enlem, boylam) döndürür."""
    print("\n  Mevcut şehirler:")
    adlar = sorted(astro.SEHIRLER.keys())
    for i in range(0, len(adlar), 4):
        print("    " + "  ".join(f"{a:12s}" for a in adlar[i:i + 4]))
    while True:
        ham = input("\n  Doğum yeriniz (şehir adı, ya da 'enlem,boylam'): ").strip().lower()
        if ham in astro.SEHIRLER:
            return astro.SEHIRLER[ham]
        if "," in ham:
            try:
                enlem, boylam = (float(x) for x in ham.split(","))
                return enlem, boylam
            except ValueError:
                pass
        print("  ! Tanınmayan şehir. Liste dışı için 'enlem,boylam' girin (örn 41.0,28.9).")


def utc_al():
    ham = input("  Saat dilimi (UTC farkı, Türkiye için 3) [varsayılan 3]: ").strip()
    if not ham:
        return 3.0
    try:
        return float(ham.replace(",", "."))
    except ValueError:
        print("  ! Geçersiz; 3 kullanılıyor.")
        return 3.0


def yukselen_gercek():
    """Swiss Ephemeris ile gerçek yükselen + doğum haritası."""
    gun, ay, yil = tarih_al()
    saat, dakika = saat_al()
    enlem, boylam = sehir_al()
    utc = utc_al()

    burc_yazdir(burc_bul(ay, gun), "Güneş Burcunuz")

    yuk_ad, yuk_derece, _ = astro.yukselen_hesapla(
        yil, ay, gun, saat, dakika, enlem, boylam, utc
    )
    yuk = next(b for b in BURCLAR if b[0] == yuk_ad)
    print(f"  Yükselen Burcunuz: {yuk_ad} ({yuk_derece:.1f}°)")
    print(f"    {yuk[4]}\n")

    print("  --- Doğum Haritası (Gezegen Konumları) ---")
    for ad, burc, derece in astro.gezegen_konumlari(yil, ay, gun, saat, dakika, utc):
        print(f"    {ad:8s}: {burc:8s} {derece:5.1f}°")
    print()


def burc_sec(mesaj):
    """Geçerli bir burç adı alana kadar sorar."""
    while True:
        ad = input(mesaj).strip().lower()
        bulundu = next((b[0] for b in BURCLAR if b[0].lower() == ad), None)
        if bulundu:
            return bulundu
        print("  ! Geçerli bir burç adı girin (örn Koç, Akrep, İkizler).")


def uyum_menu():
    print("\n  İki burcun uyumunu öğrenin.")
    b1 = burc_sec("  1. burç: ")
    b2 = burc_sec("  2. burç: ")
    uyum_mod.uyum_yazdir(b1, b2)
    if input("  Tüm uyum matrisini görmek ister misiniz? (e/h): ").strip().lower() == "e":
        uyum_mod.tablo_yazdir()


def yorum_menu():
    burc = burc_sec("  Burcunuz: ")
    print("\n  1) Günlük yorum")
    print("  2) Haftalık yorum")
    s = input("  Seçiminiz: ").strip()
    if s == "2":
        yorum_mod.haftalik_yazdir(burc)
    else:
        yorum_mod.gunluk_yazdir(burc)


def menu():
    print("=" * 50)
    print("              BURÇ UYGULAMASI")
    print("=" * 50)
    while True:
        print("\n  1) Doğum tarihimden burcumu bul")
        print("  2) Yükselen burcumu + doğum haritamı hesapla")
        print("  3) Tüm burçları listele")
        print("  4) Belirli bir burç hakkında bilgi")
        print("  5) Burç uyumu (sinastri)")
        print("  6) Günlük / haftalık yorum")
        print("  0) Çıkış")
        secim = input("\n  Seçiminiz: ").strip()

        if secim == "1":
            gun, ay, yil = tarih_al()
            burc_yazdir(burc_bul(ay, gun))

        elif secim == "2":
            if ASTRO_VAR:
                yukselen_gercek()
            else:
                print("\n  ! 'pyswisseph' kurulu değil; yaklaşık hesap kullanılıyor.")
                print("    Kurmak için: python -m pip install pyswisseph\n")
                gun, ay, yil = tarih_al()
                saat, dakika = saat_al()
                burc_yazdir(burc_bul(ay, gun), "Güneş Burcunuz")
                burc_yazdir(yukselen_burc(ay, gun, saat, dakika), "Yaklaşık Yükselen Burcunuz")

        elif secim == "3":
            tum_burclari_listele()

        elif secim == "4":
            ad = input("  Burç adı (örn Koç): ").strip().lower()
            bulundu = next((b for b in BURCLAR if b[0].lower() == ad), None)
            if bulundu:
                burc_yazdir(bulundu, "Burç")
            else:
                print("  ! Böyle bir burç bulunamadı.")

        elif secim == "5":
            if EK_VAR:
                uyum_menu()
            else:
                print("  ! uyum.py bulunamadı.")

        elif secim == "6":
            if EK_VAR:
                yorum_menu()
            else:
                print("  ! yorum.py bulunamadı.")

        elif secim == "0":
            print("\n  Görüşmek üzere! ✦\n")
            break
        else:
            print("  ! Geçersiz seçim.")


if __name__ == "__main__":
    menu()
