# -*- coding: utf-8 -*-
"""
transit.py — GERÇEK transit (gezegen geçişi) yorumu.

Şablon değildir: bugünkü gezegen konumlarını (transit), kişinin doğum
haritasındaki gezegen ve yükselen konumlarıyla karşılaştırır; aralarında
oluşan açıları (kavuşum, sekstil, kare, üçgen, karşıt) bulup yorumlar.

Swiss Ephemeris (pyswisseph) gerektirir.
"""

from datetime import date
import swisseph as swe

import astro  # _julian_day, _burc_ve_derece, GEZEGENLER, harita_detay


# Açı tanımları: hedef derece -> (ad, orb, ton)
ACILAR = [
    (0,   "Kavuşum", 5, "yoğunlaştırıcı"),
    (60,  "Sekstil", 4, "destekleyici"),
    (90,  "Kare",    4, "zorlayıcı"),
    (120, "Üçgen",   4, "akıcı"),
    (180, "Karşıt",  5, "gerilimli"),
]

# Transit gezegenin getirdiği tema
TRANSIT_TEMA = {
    "Güneş":   "kimlik, canlılık ve odak",
    "Ay":      "duygular ve ruh hali",
    "Merkür":  "iletişim, zihin ve kararlar",
    "Venüs":   "aşk, ilişkiler ve para",
    "Mars":    "enerji, girişim ve tutku",
    "Jüpiter": "şans, büyüme ve fırsat",
    "Satürn":  "sorumluluk, disiplin ve sınırlar",
    "Uranüs":  "değişim, özgürlük ve sürprizler",
    "Neptün":  "hayal, sezgi ve ilham",
    "Plüton":  "dönüşüm ve derin değişim",
}

# Doğum haritasındaki noktanın temsil ettiği yaşam alanı
NATAL_ALAN = {
    "Güneş":   "öz benliğini ve hedeflerini",
    "Ay":      "duygusal dünyanı ve ev yaşamını",
    "Merkür":  "düşünce ve iletişimini",
    "Venüs":   "ilişkilerini ve zevklerini",
    "Mars":    "enerjini ve girişimlerini",
    "Jüpiter": "büyüme ve şans alanlarını",
    "Satürn":  "sorumluluk ve kariyer yapını",
    "Uranüs":  "özgünlük ve değişim isteğini",
    "Neptün":  "hayal ve sezgilerini",
    "Plüton":  "dönüşüm süreçlerini",
    "Yükselen": "dış görünüşünü ve genel duruşunu",
}

# Açıya göre cümle kalıbı
ACI_KALIP = {
    "Kavuşum": "{tt} teması {na} doğrudan etkiliyor; yeni bir başlangıç ya da yoğunlaşma zamanı.",
    "Sekstil": "{tt} alanı {na} destekliyor; fırsatları değerlendirmek için uygun.",
    "Üçgen":   "{tt} enerjisi {na} kolayca besliyor; akış ve uyum mümkün.",
    "Kare":    "{tt} kaynaklı gerginlik {na} zorluyor; sabır ve esneklik gerekebilir.",
    "Karşıt":  "{tt} ile {na} arasında denge arayışı; karşıt güçler gündemde.",
}

# Önem ağırlığı (sıralama için): yavaş gezegenlerin transiti daha kalıcı/önemli
GEZ_AGIRLIK = {
    "Plüton": 10, "Neptün": 9, "Uranüs": 8, "Satürn": 7, "Jüpiter": 6,
    "Mars": 5, "Venüs": 4, "Merkür": 3, "Güneş": 2, "Ay": 1,
}


def _gezegen_boylamlari(jd):
    """Verilen Julian Day için {gezegen: mutlak_boylam} döndürür."""
    sonuc = {}
    for ad, pid in astro.GEZEGENLER:
        konum, _ = swe.calc_ut(jd, pid)
        sonuc[ad] = konum[0] % 360.0
    return sonuc


def _aci_bul(boy1, boy2):
    """İki boylam arasındaki açı eşleşmesini döndürür ya da None."""
    fark = abs(boy1 - boy2) % 360.0
    if fark > 180:
        fark = 360 - fark
    for hedef, ad, orb, ton in ACILAR:
        sapma = abs(fark - hedef)
        if sapma <= orb:
            return {"aci": ad, "ton": ton, "orb": round(sapma, 1)}
    return None


def gunluk_transit(yil, ay, gun, saat, dakika, enlem, boylam,
                   utc_offset=3.0, hedef_gun=None, en_fazla=7):
    """
    Doğum verileri + hedef gün için gerçek transit yorumlarını döndürür.
    hedef_gun verilmezse bugünü kullanır.
    """
    if hedef_gun is None:
        hedef_gun = date.today()

    # 1) Doğum haritası (natal) noktaları — mutlak boylamlar
    natal = astro.harita_detay(yil, ay, gun, saat, dakika, enlem, boylam, utc_offset)
    natal_noktalar = {g["ad"]: g["boylam"] for g in natal["gezegenler"]}
    natal_noktalar["Yükselen"] = natal["yukselen"]["boylam"]

    # 2) Hedef günün transit gezegen konumları (gün ortası, UT)
    jd_transit = astro._julian_day(
        hedef_gun.year, hedef_gun.month, hedef_gun.day, 12, 0, utc_offset
    )
    transit_boy = _gezegen_boylamlari(jd_transit)

    # 3) Transit x Natal açılarını tara
    bulgular = []
    for t_ad, t_boy in transit_boy.items():
        for n_ad, n_boy in natal_noktalar.items():
            eslesme = _aci_bul(t_boy, n_boy)
            if not eslesme:
                continue
            kalip = ACI_KALIP[eslesme["aci"]]
            metin = kalip.format(
                tt=TRANSIT_TEMA[t_ad].capitalize(),
                na=NATAL_ALAN.get(n_ad, n_ad),
            )
            bulgular.append({
                "transit": t_ad,
                "natal": n_ad,
                "aci": eslesme["aci"],
                "ton": eslesme["ton"],
                "orb": eslesme["orb"],
                "metin": metin,
                "_skor": GEZ_AGIRLIK[t_ad] * 2 - eslesme["orb"],
            })

    # Önemliden önemsize sırala, en fazla N tanesini al
    bulgular.sort(key=lambda b: b["_skor"], reverse=True)
    bulgular = bulgular[:en_fazla]
    for b in bulgular:
        b.pop("_skor", None)

    # Transit gezegenlerin o günkü burçları (özet)
    transit_ozet = []
    for ad, boy in transit_boy.items():
        burc, derece = astro._burc_ve_derece(boy)
        transit_ozet.append({"ad": ad, "burc": burc, "derece": round(derece, 1)})

    return {
        "tarih": hedef_gun.isoformat(),
        "yukselen": natal["yukselen"],
        "transit_gezegenler": transit_ozet,
        "yorumlar": bulgular,
    }


def yazdir(sonuc):
    print(f"\n  ╔══ Gerçek Transit Yorumu — {sonuc['tarih']} ══╗\n")
    if not sonuc["yorumlar"]:
        print("  Bugün doğum haritanla belirgin bir açı oluşmuyor; sakin bir gün.\n")
    for b in sonuc["yorumlar"]:
        print(f"  • {b['transit']} {b['aci']} natal {b['natal']} "
              f"(orb {b['orb']}°, {b['ton']})")
        print(f"      {b['metin']}")
    print()


if __name__ == "__main__":
    enlem, boylam = astro.SEHIRLER["istanbul"]
    s = gunluk_transit(1990, 4, 25, 14, 30, enlem, boylam, 3.0)
    yazdir(s)
