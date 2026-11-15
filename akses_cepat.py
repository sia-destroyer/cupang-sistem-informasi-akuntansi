import pandas as pd
import streamlit as st

from COA import AKUN, KAS
from akuntansi import (filter_periode, laporan_buku_besar, laporan_jurnal_umum,
                       laporan_laba_rugi, laporan_neraca_saldo, saldo_per_akun,
                       total_tipe)
from supports import judul_halaman, pilih_periode, rp, tombol_excel, format_uang
from database import muat_jurnal

def halaman_akses_cepat():
    judul_halaman("Akses Cepat", "Laporan akuntansi: jurnal umum, buku besar, laba rugi, dan neraca saldo.")
    df = muat_jurnal()

    # Filter tanggal untuk semua laporan
    awal, akhir = pilih_periode("aq", "Tahun ini")
    df_p = filter_periode(df, awal, akhir)        # data dalam periode
    df_sd = filter_periode(df, None, akhir)       # data sampai tanggal akhir

    # Siapkan semua laporan (juga dipakai untuk Excel)
    jurnal = laporan_jurnal_umum(df_p)
    laba_rugi = laporan_laba_rugi(df_p)
    neraca = laporan_neraca_saldo(df_sd)
    buku_besar_semua = pd.concat(
        [laporan_buku_besar(df_sd, k).assign(Akun=f"{k} - {AKUN[k]['nama']}") for k in AKUN],
        ignore_index=True)

    # Ringkasan singkat periode
    laba = total_tipe(saldo_per_akun(df_p), "Pendapatan") - total_tipe(saldo_per_akun(df_p), "Beban")
    m = st.columns(3)
    m[0].metric("Laba (Rugi) periode", rp(laba), border=True)
    m[1].metric("Jumlah transaksi", f"{df_p['bukti'].nunique()}", border=True)
    m[2].metric("Kas di Bank", rp(saldo_per_akun(df_sd)[KAS]), border=True)

    # Unduh semua laporan
    with st.container(border=True):
        teks, tombol = st.columns([3, 1], vertical_alignment="center")
        teks.markdown("**Unduh laporan lengkap**")
        teks.caption("Jurnal umum, buku besar, laba rugi, dan neraca saldo dalam satu file Excel.")
        with tombol:
            tombol_excel("⬇️ Unduh SEMUA laporan ke Excel",
                         {"Jurnal Umum": jurnal, "Buku Besar": buku_besar_semua,
                          "Laba Rugi": laba_rugi, "Neraca Saldo": neraca},
                         "laporan_akuntansi.xlsx", "xl_semua")

    tab1, tab2, tab3, tab4 = st.tabs(["Jurnal Umum", "Buku Besar", "Laba Rugi", "Neraca Saldo"])

    with tab1:
        st.dataframe(format_uang(jurnal, ["Debit", "Kredit"]), hide_index=True)
        tombol_excel("⬇️ Excel", {"Jurnal Umum": jurnal}, "jurnal_umum.xlsx", "xl_jurnal")

    with tab2:
        # format_func = cara menampilkan pilihan (nilai aslinya tetap kode akun)
        kode = st.selectbox("Pilih akun", list(AKUN), key="bb_akun",
                            format_func=lambda k: f"{k} - {AKUN[k]['nama']}")
        bb = laporan_buku_besar(df_sd, kode)
        st.caption(f"Saldo normal: {'Debit' if AKUN[kode]['normal'] == 'D' else 'Kredit'}")
        st.dataframe(format_uang(bb, ["Debit", "Kredit", "Saldo"]), hide_index=True)
        tombol_excel("⬇️ Excel", {AKUN[kode]["nama"]: bb}, f"buku_besar_{kode}.xlsx", "xl_bb")

    with tab3:
        st.dataframe(format_uang(laba_rugi, ["Jumlah"]), hide_index=True)
        tombol_excel("⬇️ Excel", {"Laba Rugi": laba_rugi}, "laba_rugi.xlsx", "xl_lr")

    with tab4:
        st.dataframe(format_uang(neraca, ["Debit", "Kredit"]), hide_index=True)
        total = neraca.iloc[-1]                  # baris terakhir = TOTAL
        if total["Debit"] == total["Kredit"]:
            st.success("Seimbang ✅ (total Debit = total Kredit)")
        else:
            st.error("Tidak seimbang ❌ — periksa jurnal")
        tombol_excel("⬇️ Excel", {"Neraca Saldo": neraca}, "neraca_saldo.xlsx", "xl_ns")
