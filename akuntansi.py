"""Perhitungan akuntansi dan penyusunan laporan SiCupang."""

import pandas as pd

from COA import AKUN

# =====================================================================
# 4. PERHITUNGAN AKUNTANSI
# =====================================================================
def saldo_per_akun(df):
    """Hitung saldo tiap akun. Saldo dihitung sesuai sisi normalnya:
       akun normal Debit  -> saldo = debit - kredit
       akun normal Kredit -> saldo = kredit - debit
    Hasil: {"1-101": 5000000, ...}"""
    hasil = {}
    for kode, info in AKUN.items():
        d = int(df.loc[df["kode_akun"] == kode, "debit"].sum())
        k = int(df.loc[df["kode_akun"] == kode, "kredit"].sum())
        hasil[kode] = d - k if info["normal"] == "D" else k - d
    return hasil


def total_tipe(saldo, tipe):
    """Jumlahkan saldo semua akun bertipe tertentu (mis. 'Pendapatan')."""
    # sum(... for ... if ...) = jumlahkan hanya yang memenuhi syarat 'if'
    return sum(s for kode, s in saldo.items() if AKUN[kode]["tipe"] == tipe)


def filter_periode(df, awal=None, akhir=None):
    """Ambil baris jurnal pada rentang tanggal tertentu."""
    if awal is not None:
        df = df[df["tanggal"] >= awal]
    if akhir is not None:
        df = df[df["tanggal"] <= akhir]
    return df


def laporan_jurnal_umum(df):
    """Jurnal umum: urut tanggal, akun kredit dijorok ke kanan (aturan penulisan jurnal)."""
    j = pd.DataFrame({
        "Tanggal": df["tanggal"],
        "Bukti": df["bukti"].str[:8],
        "Keterangan": df["keterangan"],
        # kalau sisi kredit > 0, tambahkan spasi di depan nama akun
        "Akun": [("      " + a) if k > 0 else a for a, k in zip(df["akun"], df["kredit"])],
        "Debit": df["debit"],
        "Kredit": df["kredit"],
    })
    return j.reset_index(drop=True)


def laporan_buku_besar(df, kode):
    """Buku besar satu akun + saldo berjalan."""
    d = df[df["kode_akun"] == kode].sort_values(["tanggal", "id"])
    normal = AKUN[kode]["normal"]
    saldo, baris = 0, []
    for _, r in d.iterrows():        # iterrows = ulangi tiap baris tabel
        saldo += (r["debit"] - r["kredit"]) if normal == "D" else (r["kredit"] - r["debit"])
        baris.append({"Tanggal": r["tanggal"], "Keterangan": r["keterangan"],
                      "Debit": r["debit"], "Kredit": r["kredit"], "Saldo": saldo})
    return pd.DataFrame(baris, columns=["Tanggal", "Keterangan", "Debit", "Kredit", "Saldo"])


def laporan_neraca_saldo(df):
    """Neraca saldo (trial balance): saldo akhir tiap akun di kolom Debit ATAU Kredit.
    Total Debit harus sama dengan total Kredit."""
    baris = []
    for kode, info in AKUN.items():
        d = int(df.loc[df["kode_akun"] == kode, "debit"].sum())
        k = int(df.loc[df["kode_akun"] == kode, "kredit"].sum())
        if d == 0 and k == 0:
            continue                  # akun tanpa transaksi tidak ditampilkan
        net = d - k
        baris.append({"Kode": kode, "Akun": info["nama"],
                      "Debit": net if net > 0 else 0,
                      "Kredit": -net if net < 0 else 0})
    t = pd.DataFrame(baris, columns=["Kode", "Akun", "Debit", "Kredit"])
    total = pd.DataFrame([{"Kode": "", "Akun": "TOTAL",
                           "Debit": t["Debit"].sum(), "Kredit": t["Kredit"].sum()}])
    return pd.concat([t, total], ignore_index=True)


def laporan_laba_rugi(df):
    """Laporan laba rugi (income statement) dari akun Pendapatan & Beban."""
    saldo = saldo_per_akun(df)
    baris = []                          # tiap item: (keterangan, jumlah)

    def seksi(judul, tipe):             # fungsi di dalam fungsi (hanya dipakai di sini)
        baris.append((judul, None))
        for kode, info in AKUN.items():
            if info["tipe"] == tipe and saldo[kode] != 0:
                baris.append(("    " + info["nama"], saldo[kode]))
        total = total_tipe(saldo, tipe)
        baris.append((f"Total {judul.title()}", total))
        return total

    pendapatan = seksi("PENDAPATAN", "Pendapatan")
    beban = seksi("BEBAN", "Beban")
    baris.append(("LABA (RUGI) BERSIH", pendapatan - beban))
    return pd.DataFrame(baris, columns=["Keterangan", "Jumlah"])

# =====================================================================
# Penyusunan jurnal dan rincian saldo awal
# =====================================================================
def entri_saldo_awal(d):
    """Susun jurnal saldo awal:
       Debit  : kas, piutang, persediaan, perlengkapan, peralatan
       Kredit : utang bank, utang orang
       Modal  : selisihnya (aset - utang) supaya jurnal seimbang."""
    saldo = {}                                        # kode akun -> jumlah

    def tambah(kode, jumlah):
        if jumlah:
            saldo[kode] = saldo.get(kode, 0) + jumlah  # .get(x, 0) = ambil x, kalau tak ada pakai 0

    total = lambda daftar: sum(r["nominal"] for r in daftar)
    tambah("1-101", d["kas"])
    tambah("1-102", total(d["piutang"]))
    tambah("1-103", total(d["ikan"]))
    tambah("1-104", total(d["pakan"]))
    tambah("1-105", total(d["obat"]))
    tambah("1-106", total(d["lainnya"]))
    tambah("1-107", total(d["perlengkapan"]))
    tambah("1-108", total(d["peralatan"]))
    for r in d["utang"]:
        tambah("2-101" if r["pihak"] == "Bank" else "2-102", r["nominal"])

    entri = []
    for kode, jml in saldo.items():
        if AKUN[kode]["normal"] == "D":
            entri.append((kode, jml, 0))              # akun normal debit -> di sisi debit
        else:
            entri.append((kode, 0, jml))              # akun normal kredit -> di sisi kredit
    selisih = sum(e[1] for e in entri) - sum(e[2] for e in entri)
    if selisih > 0:
        entri.append(("3-101", 0, selisih))           # aset > utang: modal di kredit
    elif selisih < 0:
        entri.append(("3-101", -selisih, 0))          # utang > aset: modal negatif (debit)
    return entri


def item_saldo_awal(d):
    """Rincian saldo awal (jenis ikan, harga, umur pemakaian, dll) untuk tabel saldo_awal_item."""
    items = []
    if d["kas"]:
        items.append({"kelompok": "kas_bank", "pihak": None, "nama": "Kas di bank",
                      "nominal": d["kas"], "umur_bulan": None})
    for kelompok in ("utang", "piutang", "ikan", "pakan", "obat", "lainnya",
                     "peralatan", "perlengkapan"):
        for r in d[kelompok]:
            items.append({"kelompok": kelompok, "pihak": r.get("pihak"), "nama": r["nama"],
                          "nominal": r["nominal"], "umur_bulan": r.get("umur")})
    return items
