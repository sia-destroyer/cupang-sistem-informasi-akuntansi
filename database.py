"""Akses database Supabase dan fungsi penyimpanan data SiCupang."""

# ---------- IMPORT (memanggil library yang dipakai) ----------
import uuid                     # membuat kode unik untuk bukti jurnal

import pandas as pd
import streamlit as st
from supabase import create_client

from COA import AKUN
from akuntansi import entri_saldo_awal, item_saldo_awal

# ---------- Koneksi Supabase ----------
@st.cache_resource          # dibuat sekali lalu dipakai ulang (tidak membuat koneksi baru tiap klik)
def _buat_client(url, key):
    return create_client(url, key)


def get_client():
    """Ambil koneksi Supabase (pakai service_role key dari secrets.toml)."""
    try:
        return _buat_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])
    except Exception:
        st.error("Isi SUPABASE_URL dan SUPABASE_SERVICE_KEY di .streamlit/secrets.toml")
        st.stop()                      # hentikan program di sini


def uid():
    """ID akun yang sedang login. Dipakai di SEMUA query supaya data antar akun tidak tercampur."""
    return st.session_state.user["id"]

# =====================================================================
# 3. DATABASE: ambil & simpan jurnal
# =====================================================================
KOLOM_JURNAL = ["id", "bukti", "tanggal", "keterangan", "jenis", "kode_akun", "debit", "kredit"]


def ambil_semua(tabel):
    """Ambil semua baris tabel. Supabase membatasi 1000 baris per permintaan,
    jadi kita ambil bertahap (halaman demi halaman)."""
    hasil, mulai = [], 0
    while True:
        res = get_client().table(tabel).select("*").eq("user_id", uid()).order("id").range(mulai, mulai + 999).execute()
        hasil += res.data
        if len(res.data) < 1000:
            break
        mulai += 1000
    return hasil


def muat_jurnal():
    """Ambil seluruh jurnal user sebagai DataFrame. Disimpan sementara (cache)
    di session_state supaya tidak query berulang tiap klik."""
    if "jurnal_df" not in st.session_state:
        df = pd.DataFrame(ambil_semua("jurnal"), columns=KOLOM_JURNAL)
        df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date
        df[["debit", "kredit"]] = df[["debit", "kredit"]].astype("int64")
        df["akun"] = df["kode_akun"].map(lambda k: f"{k} - {AKUN[k]['nama']}")
        st.session_state.jurnal_df = df.sort_values(["tanggal", "id"]).reset_index(drop=True)
    return st.session_state.jurnal_df


def bersihkan_cache():
    """Hapus cache jurnal -> data diambil ulang dari database di pemuatan berikutnya."""
    st.session_state.pop("jurnal_df", None)


def baris_jurnal(tanggal, keterangan, jenis, entri):
    """Bentuk baris jurnal siap simpan.
    entri = daftar (kode_akun, debit, kredit). Wajib seimbang!"""
    total_d = sum(e[1] for e in entri)
    total_k = sum(e[2] for e in entri)
    if total_d != total_k:
        raise ValueError(f"Jurnal tidak seimbang: debit {total_d} != kredit {total_k}")
    bukti = str(uuid.uuid4())   # satu kode untuk semua baris dalam satu transaksi
    # 'for kode, d, k in entri' = membongkar tiap tuple (kode, debit, kredit)
    return [
        {"user_id": uid(), "bukti": bukti, "tanggal": tanggal.isoformat(), "keterangan": keterangan,
         "jenis": jenis, "kode_akun": kode, "debit": int(d), "kredit": int(k)}
        for kode, d, k in entri
    ]


def simpan_transaksi(tanggal, keterangan, jenis, entri):
    """Simpan satu transaksi (beberapa baris jurnal sekaligus) ke Supabase."""
    get_client().table("jurnal").insert(baris_jurnal(tanggal, keterangan, jenis, entri)).execute()
    bersihkan_cache()

# ---------- Status saldo awal ----------
def saldo_awal_selesai():
    """Cek di database: apakah akun ini sudah menyelesaikan saldo awal?"""
    res = (get_client().table("profil").select("saldo_awal_selesai")
           .eq("user_id", uid()).execute())
    return bool(res.data and res.data[0]["saldo_awal_selesai"])

# ---------- Penyimpanan saldo awal ----------
def simpan_saldo_awal(d, tanggal):
    """Simpan saldo awal ke Supabase: jurnal + rincian + tanda 'selesai'."""
    sb = get_client()
    u = uid()
    entri = entri_saldo_awal(d)
    # hapus sisa percobaan sebelumnya milik akun ini (jika sempat gagal di tengah jalan)
    sb.table("jurnal").delete().eq("user_id", u).eq("jenis", "saldo_awal").execute()
    sb.table("saldo_awal_item").delete().eq("user_id", u).execute()
    if entri:
        sb.table("jurnal").insert(
            baris_jurnal(tanggal, "Saldo awal", "saldo_awal", entri)).execute()
    items = [{**it, "user_id": u} for it in item_saldo_awal(d)]   # tambahkan user_id ke tiap baris
    if items:
        sb.table("saldo_awal_item").insert(items).execute()
    # terakhir: tandai selesai (upsert = insert, atau update jika sudah ada)
    sb.table("profil").upsert({"user_id": u, "saldo_awal_selesai": True}).execute()
    bersihkan_cache()
    st.session_state.sa_selesai = True
    st.session_state.pop("sa", None)
