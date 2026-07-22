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

# Burç -> element (element temelli çeşni cümleleri için)
BURC_ELEMENT = {
    "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
    "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
    "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
    "Yengeç": "Su", "Akrep": "Su", "Balık": "Su",
}

# Yaşam alanı -> cümle havuzu (çeşitlilik için genişletildi)
HAVUZ = {
    "Genel": [
        "Enerjin yüksek; bugün başladığın işler hızla ilerleyebilir.",
        "Sakin bir gün seni bekliyor; aceleci kararlardan kaçın.",
        "Beklenmedik bir haber günün akışını değiştirebilir.",
        "İçgüdülerine güven; sezgilerin bugün oldukça güçlü.",
        "Küçük bir aksilik morali bozmasın, akşama doğru düzelecek.",
        "Yeni bir başlangıç için uygun bir gün; cesur ol.",
        "Bugün detaylara dikkat etmek seni olası bir hatadan kurtarır.",
        "Uzun süredir ertelediğin bir işi bitirmek için ideal bir gün.",
        "Çevrendekilerin desteği bugün beklediğinden fazla olacak.",
        "Planlarını esnek tut; gün içinde işler yön değiştirebilir.",
        "Kendine küçük bir mola ver; zihnin berraklaştıkça çözümler netleşir.",
        "Bugün attığın küçük bir adım ilerideki büyük bir kapıyı aralayabilir.",
    ],
    "Aşk": [
        "İlişkinde içten bir konuşma bağını güçlendirecek.",
        "Bekarsan ilgi çekici biriyle yolların kesişebilir.",
        "Partnerine kulak vermek bugün huzur getirir.",
        "Romantik bir sürpriz günü renklendirebilir.",
        "Geçmişten biri yeniden gündeme gelebilir; temkinli ol.",
        "Duygularını ifade etmek için doğru zaman.",
        "Küçük bir jest, sevdiğin kişiyle aranı belirgin şekilde tazeleyebilir.",
        "Bugün empati kurmak, olası bir kırgınlığı baştan önleyecek.",
        "Sosyal bir ortamda tanışacağın biri dikkatini çekebilir.",
        "İlişkinde dürüstlük bugün en güçlü kozun olacak.",
        "Kendine ayırdığın zaman, ikili ilişkilerine de olumlu yansıyacak.",
        "Beklenmedik bir yakınlaşma günü heyecanlandırabilir.",
    ],
    "Kariyer & Para": [
        "İş yerinde fikirlerin takdir görecek, öne çık.",
        "Bütçeni gözden geçir; gereksiz harcamalara dikkat.",
        "Beklediğin bir fırsat kapını çalabilir, hazır ol.",
        "Ekip çalışması bugün sana avantaj sağlayacak.",
        "Sabırlı ol; sonuçlar düşündüğünden biraz geç gelebilir.",
        "Küçük bir kazanç ya da olumlu bir gelişme mümkün.",
        "Bir üstünle ya da yetkiliyle kuracağın iletişim işine yarayacak.",
        "Uzun vadeli bir yatırımı araştırmak için doğru zaman.",
        "Bugün disiplinli çalışman gözlerden kaçmayacak.",
        "Yeni bir iş bağlantısı ileride değer kazanabilir.",
        "Riskli bir harcamayı bir gün ertelemek sana iyi gelecek.",
        "Yaratıcı bir çözüm, tıkanan bir işi yeniden hareketlendirebilir.",
    ],
    "Sağlık & Enerji": [
        "Bol su iç ve kısa bir yürüyüş enerjini toplar.",
        "Dinlenmeye öncelik ver; vücudun mola istiyor.",
        "Zihnini boşaltmak için nefes egzersizleri iyi gelir.",
        "Hareketli bir gün; formunu korumak için ideal.",
        "Uyku düzenine dikkat et, yorgunluk birikmiş olabilir.",
        "Sağlıklı beslenme bugün kendini iyi hissettirecek.",
        "Doğada geçireceğin kısa bir zaman zihnini tazeleyecek.",
        "Esneme hareketleri gün boyu biriken gerginliği çözecek.",
        "Kafein yerine bitki çayı bugün dengeni koruyabilir.",
        "Bedeninin verdiği sinyalleri dinle; küçük bir molaya ihtiyacın var.",
        "Erken yatmak yarına çok daha dinç başlamanı sağlayacak.",
        "Kısa bir dijital detoks zihinsel enerjini yükseltecek.",
    ],
}

# Element -> günün "eleman notu" (burcun elementine göre eklenir)
ELEMENT_NOT = {
    "Ateş": [
        "Ateş elementin bugün girişkenliğini artırıyor; inisiyatif al.",
        "İçindeki kıvılcım yüksek; enerjini doğru hedefe yönlendir.",
    ],
    "Toprak": [
        "Toprak elementin bugün seni sağlam ve gerçekçi tutuyor.",
        "Sabrın ve istikrarın bugün en güçlü yanların.",
    ],
    "Hava": [
        "Hava elementin zihnini keskinleştiriyor; iletişimde parlıyorsun.",
        "Fikir alışverişi bugün sana yeni kapılar açabilir.",
    ],
    "Su": [
        "Su elementin sezgilerini güçlendiriyor; iç sesine kulak ver.",
        "Duygusal derinliğin bugün çevrendekilere şifa olabilir.",
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
    element = BURC_ELEMENT.get(burc)
    eleman_not = _secim(ELEMENT_NOT[element], burc, iso, "eleman") if element else None
    return {
        "burc": burc,
        "tarih": iso,
        "element": element,
        "eleman_not": eleman_not,
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
