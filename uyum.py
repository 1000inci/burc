# -*- coding: utf-8 -*-
"""
uyum.py — Burç-burç uyum (sinastri) tablosu.
Klasik astrolojideki açı (aspect) mantığını kullanır:
iki burcun zodyaktaki uzaklığı aralarındaki ilişkiyi belirler.
"""

BURC_SIRA = [
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık",
]

ELEMENT = {
    "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
    "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
    "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
    "Yengeç": "Su", "Akrep": "Su", "Balık": "Su",
}

# uzaklık (0-6) -> (açı adı, yıldız puanı 1-5, kısa yorum)
ACILAR = {
    0: ("Kavuşum",   4, "Aynı burç: güçlü benzerlik ve anlayış, ama bazen fazla benzemekten sıkılma."),
    1: ("Yarım-sekstil", 2, "Komşu burçlar: farklı bakış açıları, uyum için çaba gerekir."),
    2: ("Sekstil",   4, "Doğal bir dostluk ve akıcı iletişim; birbirini destekler."),
    3: ("Kare",      2, "Gerilim ve sürtüşme; çekici ama zorlayıcı, büyüme potansiyeli yüksek."),
    4: ("Üçgen",     5, "En uyumlu açı: aynı element, doğal akış ve derin uyum."),
    5: ("Altmış-beşli (Quincunx)", 2, "Uyumsuz görünen ama tamamlayıcı; sürekli ayar gerektirir."),
    6: ("Karşıt",    3, "Kutupsal çekim: zıt kutuplar birbirini hem çeker hem zorlar."),
}


def _uzaklik(b1, b2):
    i, j = BURC_SIRA.index(b1), BURC_SIRA.index(b2)
    fark = abs(i - j)
    return min(fark, 12 - fark)


def uyum(b1, b2):
    """İki burç için (açı_adı, puan, yorum, element_ilişkisi) döndürür."""
    d = _uzaklik(b1, b2)
    aci, puan, yorum = ACILAR[d]
    e1, e2 = ELEMENT[b1], ELEMENT[b2]
    if e1 == e2:
        el = f"Aynı element ({e1}) — benzer mizaç."
    elif {e1, e2} in ({"Ateş", "Hava"}, {"Toprak", "Su"}):
        el = f"{e1} + {e2} — birbirini besleyen elementler."
    else:
        el = f"{e1} + {e2} — zorlayıcı element karışımı."
    return aci, puan, yorum, el


def yildiz(puan):
    return "★" * puan + "☆" * (5 - puan)


def uyum_yazdir(b1, b2):
    aci, puan, yorum, el = uyum(b1, b2)
    print(f"\n  {b1} ♥ {b2}")
    print(f"  Uyum    : {yildiz(puan)}  ({puan}/5)")
    print(f"  Açı     : {aci}")
    print(f"  Element : {el}")
    print(f"  Yorum   : {yorum}\n")


def tablo_yazdir():
    """Tüm burçların birbiriyle uyum puanı matrisi (1-5)."""
    kisa = {b: b[:3] for b in BURC_SIRA}
    print("\n  Uyum Matrisi (1-5 puan)\n")
    print("       " + " ".join(f"{kisa[b]:>3s}" for b in BURC_SIRA))
    for b1 in BURC_SIRA:
        satir = []
        for b2 in BURC_SIRA:
            _, puan, _, _ = uyum(b1, b2)
            satir.append(f"{puan:>3d}")
        print(f"  {kisa[b1]:>4s} " + " ".join(satir))
    print("\n  (5 = en uyumlu)\n")


if __name__ == "__main__":
    uyum_yazdir("Koç", "Aslan")
    uyum_yazdir("Boğa", "Akrep")
    uyum_yazdir("İkizler", "Başak")
    tablo_yazdir()
