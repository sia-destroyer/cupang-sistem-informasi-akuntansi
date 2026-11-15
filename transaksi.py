from datetime import date

import streamlit as st

from COA import KAS, PILIHAN_PEMBELIAN, PILIHAN_PENJUALAN
from akuntansi import saldo_per_akun
from supports import judul_halaman, rp, tombol_excel, format_uang, tabel_transaksi
from database import muat_jurnal, simpan_transaksi

def halaman_transaksi(jenis, judul, pilihan):
    """jenis   : 'pembelian' atau 'penjualan'
       pilihan : dict {tulisan: kode akun}"""
    judul_halaman(judul, "Catat transaksi baru di kiri, riwayat terbaru ada di kanan."
                  if jenis == "pembelian" else
                  "Catat penjualan baru di kiri, riwayat terbaru ada di kanan.")

    # Wadah ringkasan dibuat dulu (supaya tampil paling atas),
    # tapi DIISI paling akhir supaya angkanya sudah memuat transaksi yang baru disimpan.
    ringkasan = st.container()

    kiri, kanan = st.columns([2, 3], gap="large")

    # ---------- Kolom kiri: form input ----------
    with kiri:
        with st.container(border=True):
            st.subheader(f"Input {judul}")
            with st.form(f"form_{jenis}", clear_on_submit=True):   # kosongkan form setelah submit
                c1, c2 = st.columns(2)
                tgl = c1.date_input("Tanggal", value=date.today())
                kategori = c2.selectbox("Kategori", list(pilihan.keys()))
                ket = st.text_input("Keterangan (nama barang / pembeli / penjual)")
                nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000, value=0)
                kirim = st.form_submit_button("Submit", type="primary")

            if kirim:
                kode = pilihan[kategori]
                if nominal <= 0:
                    st.error("Nominal harus lebih dari 0.")
                elif not ket.strip():
                    st.error("Keterangan wajib diisi.")
                elif jenis == "pembelian" and nominal > saldo_per_akun(muat_jurnal())[KAS]:
                    # cash basis: tidak bisa bayar kalau kas tidak cukup
                    st.error("Kas tidak cukup untuk pembelian ini.")
                else:
                    if jenis == "pembelian":
                        # Debit akun beban/aset, Kredit Kas (uang keluar)
                        entri = [(kode, nominal, 0), (KAS, 0, nominal)]
                    else:
                        # Debit Kas (uang masuk), Kredit Pendapatan
                        entri = [(KAS, nominal, 0), (kode, 0, nominal)]
                    try:
                        simpan_transaksi(tgl, ket.strip(), jenis, entri)
                    except Exception as e:
                        st.error(f"Gagal menyimpan: {e}")
                    else:
                        st.success(f"Tersimpan: {kategori} {rp(nominal)}")

    # ---------- Kolom kanan: 10 transaksi terbaru ----------
    with kanan:
        with st.container(border=True):
            st.subheader(f"10 {judul} Terbaru")
            tabel = tabel_transaksi(muat_jurnal(), jenis)
            if tabel.empty:
                st.info("Belum ada data.")
            else:
                st.dataframe(format_uang(tabel.head(10), ["Nominal"]), hide_index=True)
                tombol_excel("⬇️ Unduh semua ke Excel", {judul: tabel},
                             f"{jenis}.xlsx", f"xl_{jenis}")

    # ---------- Ringkasan di atas halaman (diisi terakhir) ----------
    with ringkasan:
        df = muat_jurnal()
        tabel = tabel_transaksi(df, jenis)
        bulan_ini = tabel[tabel["Tanggal"] >= date.today().replace(day=1)]
        m = st.columns(3)
        m[0].metric(f"Total {judul} bulan ini", rp(bulan_ini["Nominal"].sum()), border=True)
        m[1].metric("Jumlah transaksi bulan ini", f"{len(bulan_ini)}", border=True)
        m[2].metric("Kas di Bank", rp(saldo_per_akun(df)[KAS]), border=True)


def halaman_pembelian():
    halaman_transaksi("pembelian", "Pembelian", PILIHAN_PEMBELIAN)


def halaman_penjualan():
    halaman_transaksi("penjualan", "Penjualan", PILIHAN_PENJUALAN)
