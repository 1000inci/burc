# -*- coding: utf-8 -*-
"""
yorum.py — Günlük / haftalık burç yorumu şablonu üreteci.

Not: Bu yorumlar gerçek gezegen geçişlerine değil, tarih + burç bilgisine
göre DETERMİNİSTİK (aynı gün aynı sonucu verir) üretilen bir şablona dayanır.
Eğlence amaçlıdır. Gerçek astrolojik yorum için doğum haritası geçişleri gerekir.
"""

import hashlib
from datetime import date, timedelta

BURCLAR = [
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık",
]

# Yaşam alanı -> cümle havuzu
HAVUZ = {
    "Genel": [
        "Enerjin yüksek; bugün başladığın işler hızla ilerleyebilir.",
        "Sakin bir gün seni bekliyor; aceleci kararlardan kaçın.",
        "Beklenmedik bir haber günün akışını değiştirebilir.",
        "İçgüdülerine güven; sezgilerin bugün oldukça güçlü.",
        "Küçük bir aksilik morali bozmasın, akşama doğru düzelecek.",
        "Yeni bir başlangıç için uygun bir gün; cesur ol.",
    ],
    "Aşk": [
        "İlişkinde içten bir konuşma bağını güçlendirecek.",
        "Bekarsan ilgi çekici biriyle yolların kesişebilir.",
        "Partnerine kulak vermek bugün huzur getirir.",
        "Romantik bir sürpriz günü renklendirebilir.",
        "Geçmişten biri yeniden gündeme gelebilir; temkinli ol.",
        "Duygularını ifade etmek için doğru zaman.",
    ],
    "Kariyer & Para": [
        "İş yerinde fikirlerin takdir görecek, öne çık.",
        "Bütçeni gözden geçir; gereksiz harcamalara dikkat.",
        "Beklediğin bir fırsat kapını çalabilir, hazır ol.",
        "Ekip çalışması bugün sana avantaj sağlayacak.",
        "Sabırlı ol; sonuçlar düşündüğünden biraz geç gelebilir.",
        "Küçük bir kazanç ya da olumlu bir gelişme mümkün.",
    ],
    "Sağlık & Enerji": [
        "Bol su iç ve kısa bir yürüyüş enerjini toplar.",
        "Dinlenmeye öncelik ver; vücudun mola istiyor.",
        "Zihnini boşaltmak için nefes egzersizleri iyi gelir.",
        "Hareketli bir gün; formunu korumak için ideal.",
        "Uyku düzenine dikkat et, yorgunluk birikmiş olabilir.",
        "Sağlıklı beslenme bugün kendini iyi hissettirecek.",
    ],
}

RENKLER = ["Kırmızı", "Mavi", "Yeşil", "Mor", "Turuncu", "Beyaz", "Lacivert", "Altın", "Turkuaz", "Pembe"]
RUH_HALI = ["Coşkulu", "Sakin", "Kararlı", "Düşünceli", "İyimser", "Tutkulu", "Dengeli", "Meraklı"]


def _secim(liste, burc, gun_iso, alan, kayma=0):
    """Burç + tarih + alan'a göre deterministik seçim yapar."""
    anahtar = f"{burc}|{gun_iso}|{alan}|{kayma}"
    h = int(hashlib.md5(anahtar.encode("utf-8")).hexdigest(), 16)
    return liste[h % len(liste)]


def gunluk_yorum(burc, gun=None):
    """Tek bir gün için yorum sözlüğü döndürür."""
    if gun is None:
        gun = date.today()
    iso = gun.isoformat()
    yorumlar = {alan: _secim(cumleler, burc, iso, alan)
                for alan, cumleler in HAVUZ.items()}
    sansli_sayi = (int(hashlib.md5(f"{burc}{iso}sayi".encode()).hexdigest(), 16) % 9) + 1
    return {
        "burc": burc,
        "tarih": iso,
        "yorumlar": yorumlar,
        "sansli_sayi": sansli_sayi,
        "sansli_renk": _secim(RENKLER, burc, iso, "renk"),
        "ruh_hali": _secim(RUH_HALI, burc, iso, "ruh"),
    }


def gunluk_yazdir(burc, gun=None):
    y = gunluk_yorum(burc, gun)
    print(f"\n  ╔══ {y['burc']} — Günlük Yorum ({y['tarih']}) ══╗\n")
    for alan, metin in y["yorumlar"].items():
        print(f"  • {alan}: {metin}")
    print(f"\n  Şanslı Sayı: {y['sansli_sayi']}   Renk: {y['sansli_renk']}   "
          f"Ruh Hali: {y['ruh_hali']}\n")


def haftalik_yazdir(burc, baslangic=None):
    """Bir hafta için günlük yorumların özetini yazdırır."""
    if baslangic is None:
        # İçinde bulunulan haftanın pazartesisi
        bugun = date.today()
        baslangic = bugun - timedelta(days=bugun.weekday())
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    print(f"\n  ╔══ {burc} — Haftalık Yorum "
          f"({baslangic.isoformat()} haftası) ══╗\n")
    for i in range(7):
        g = baslangic + timedelta(days=i)
        y = gunluk_yorum(burc, g)
        # Haftalık özette her gün için bir alanı vurgula (dönüşümlü)
        alanlar = list(HAVUZ.keys())
        vurgu = alanlar[i % len(alanlar)]
        print(f"  {gunler[i]} {g.strftime('%d.%m')} | {vurgu}: {y['yorumlar'][vurgu]}")
    print()


if __name__ == "__main__":
    gunluk_yazdir("Koç")
    haftalik_yazdir("Akrep")
