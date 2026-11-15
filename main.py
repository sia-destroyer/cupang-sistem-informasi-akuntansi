"""
=====================================================================
 main.py  —  SiCupang: Aplikasi Akuntansi (CASH BASIS)
 Streamlit (tampilan, 100% Python: tanpa HTML/CSS/div) + Supabase (HANYA database, tanpa Supabase Auth)
=====================================================================

CARA MENJALANKAN
  1. pip install -r requirements.txt
  2. Jalankan isi schema.sql di Supabase (menu SQL Editor).
  3. Buat akun: ubah username/password di buat_akun.sql, lalu jalankan di SQL Editor.
     (Tidak ada menu daftar; akun hanya dibuat dari sini.)
  4. Buat file  .streamlit/secrets.toml  (di folder project) isi:
         SUPABASE_URL = "https://xxxx.supabase.co"
         SUPABASE_SERVICE_KEY = "service-role-key-anda"
     service_role key hanya dipakai di server Streamlit (tidak dikirim ke browser).
     JANGAN dibagikan / di-upload ke GitHub.
  5. streamlit run main.py

LOGIN
  Akun & password ada di tabel `akun` (password disimpan sebagai hash bcrypt).
  Pengecekan dilakukan oleh fungsi database masuk_akun(). Karena tidak memakai
  Supabase Auth, pemisahan data antar akun dilakukan aplikasi lewat kolom user_id
  (lihat fungsi uid()).

LOGIKA AKUNTANSI (CASH BASIS)
  - Pendapatan dicatat saat kas DITERIMA, beban dicatat saat kas DIBAYAR.
  - Setiap transaksi = jurnal berpasangan: total Debit == total Kredit.
  - Pembelian ikan/pakan/obat/perlengkapan/lain-lain -> BEBAN (Debit beban, Kredit Kas)
  - Pembelian peralatan                              -> ASET  (Debit Peralatan, Kredit Kas)
  - Penjualan                                        -> Debit Kas, Kredit Pendapatan
  - Saldo awal: aset (Debit) - utang (Kredit) = Modal (Kredit).

ALUR PROGRAM
  main() -> belum login?  -> halaman_login()
         -> belum isi saldo awal? -> halaman_saldo_awal()
         -> sudah?  -> st.navigation (sidebar bergrup):
                       Ringkasan: Dashboard | Transaksi: Pembelian, Penjualan | Laporan: Akses Cepat
=====================================================================
"""

# ---------- IMPORT (memanggil library yang dipakai) ----------
import streamlit as st

# Pengaturan halaman harus dipanggil sebelum komponen Streamlit lainnya.
st.set_page_config(page_title="SiCupang Akuntansi", page_icon="🐟", layout="wide",
                   initial_sidebar_state="expanded")

from akses_cepat import halaman_akses_cepat
from supports import halaman_dashboard
from database import saldo_awal_selesai
from login import halaman_login, sidebar_akun
from saldo_awal import halaman_saldo_awal
from transaksi import halaman_pembelian, halaman_penjualan

def main():
    # 1) Belum login -> tampilkan halaman login (tanpa sidebar)
    if "user" not in st.session_state:
        halaman_login()
        return

    # 2) Sudah login, tapi saldo awal belum diisi -> wizard
    if "sa_selesai" not in st.session_state:
        st.session_state.sa_selesai = saldo_awal_selesai()
    if not st.session_state.sa_selesai:
        sidebar_akun()
        halaman_saldo_awal()
        return

    # 3) Aplikasi utama: menu sidebar dikelompokkan per bagian (st.navigation)
    halaman = st.navigation({
        "Ringkasan": [
            st.Page(halaman_dashboard, title="Dashboard", icon=":material/dashboard:",
                    url_path="dashboard", default=True),
        ],
        "Transaksi": [
            st.Page(halaman_pembelian, title="Pembelian", icon=":material/shopping_cart:",
                    url_path="pembelian"),
            st.Page(halaman_penjualan, title="Penjualan", icon=":material/sell:",
                    url_path="penjualan"),
        ],
        "Laporan": [
            st.Page(halaman_akses_cepat, title="Akses Cepat", icon=":material/receipt_long:",
                    url_path="akses-cepat"),
        ],
    })
    sidebar_akun()          # kartu akun muncul di bawah menu
    halaman.run()


# Streamlit menjalankan file ini sebagai "__main__", jadi main() otomatis dipanggil
if __name__ == "__main__":
    main()
