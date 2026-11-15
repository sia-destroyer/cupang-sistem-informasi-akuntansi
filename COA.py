# =====================================================================
# 1. DAFTAR AKUN (Chart of Accounts)  —  boleh Anda tambah / ubah
# =====================================================================
# Format:  "kode": {"nama": ..., "tipe": ..., "normal": "D" atau "K"}
#   tipe   : Aset / Liabilitas / Ekuitas / Pendapatan / Beban
#   normal : sisi saldo normal akun. D = Debit, K = Kredit
AKUN = {
    "1-101": {"nama": "Kas di Bank",           "tipe": "Aset",       "normal": "D"},
    "1-102": {"nama": "Piutang",               "tipe": "Aset",       "normal": "D"},
    "1-103": {"nama": "Persediaan Ikan",       "tipe": "Aset",       "normal": "D"},
    "1-104": {"nama": "Persediaan Pakan",      "tipe": "Aset",       "normal": "D"},
    "1-105": {"nama": "Persediaan Obat",       "tipe": "Aset",       "normal": "D"},
    "1-106": {"nama": "Persediaan Lainnya",    "tipe": "Aset",       "normal": "D"},
    "1-107": {"nama": "Perlengkapan",          "tipe": "Aset",       "normal": "D"},
    "1-108": {"nama": "Peralatan",             "tipe": "Aset",       "normal": "D"},
    "2-101": {"nama": "Utang Bank",            "tipe": "Liabilitas", "normal": "K"},
    "2-102": {"nama": "Utang Orang",           "tipe": "Liabilitas", "normal": "K"},
    "3-101": {"nama": "Modal",                 "tipe": "Ekuitas",    "normal": "K"},
    "4-101": {"nama": "Penjualan Ikan",        "tipe": "Pendapatan", "normal": "K"},
    "4-102": {"nama": "Penjualan Lainnya",     "tipe": "Pendapatan", "normal": "K"},
    "5-101": {"nama": "Beban Pembelian Ikan",  "tipe": "Beban",      "normal": "D"},
    "5-102": {"nama": "Beban Pakan",           "tipe": "Beban",      "normal": "D"},
    "5-103": {"nama": "Beban Obat",            "tipe": "Beban",      "normal": "D"},
    "5-104": {"nama": "Beban Perlengkapan",    "tipe": "Beban",      "normal": "D"},
    "5-105": {"nama": "Beban Lain-lain",       "tipe": "Beban",      "normal": "D"},
}
KAS = "1-101"   # kode akun kas, dipakai di semua transaksi

# Pilihan di dropdown halaman Pembelian: "tulisan di layar": "kode akun yang di-DEBIT"
PILIHAN_PEMBELIAN = {
    "Ikan":                           "5-101",
    "Pakan":                          "5-102",
    "Obat":                           "5-103",
    "Perlengkapan":                   "5-104",
    "Peralatan (dicatat sebagai aset)": "1-108",
    "Beban lain-lain (listrik, gaji, dll)": "5-105",
}
# Pilihan di dropdown halaman Penjualan: "tulisan": "kode akun yang di-KREDIT"
PILIHAN_PENJUALAN = {
    "Penjualan Ikan":    "4-101",
    "Penjualan Lainnya": "4-102",
}
