## Cara Menjalankan Aplikasi

1. Simpan kode di atas dalam file bernama `metadata_reader.py`
2. Pastikan Anda telah menginstal semua dependensi yang diperlukan:
   ```
   pip install streamlit pillow pdfplumber olefile python-docx pandas
   ```
3. Jalankan aplikasi dengan perintah:
   ```
   streamlit run metadata_reader.py
   ```
4. Aplikasi akan terbuka di browser default Anda

## Fitur Aplikasi

1. Mendukung berbagai jenis file:
   - Gambar (JPEG, PNG) - membaca metadata EXIF
   - PDF - membaca metadata dokumen
   - Dokumen Word (DOCX dan DOC) - membaca properti dokumen

2. Tampilan user-friendly dengan:
   - Preview gambar untuk file gambar
   - Tabel metadata yang rapi
   - Penanganan error yang baik

3. Responsif dan mudah digunakan

## Deployment ke Streamlit Sharing

Untuk mendeploy aplikasi ini ke Streamlit Sharing:

1. Buat akun di [Streamlit Sharing](https://share.streamlit.io/)
2. Buat repository GitHub untuk proyek ini
3. Buat file `requirements.txt` dengan isi:
   ```
   pillow
   pdfplumber
   olefile
   python-docx
   pandas
   ```
4. Push semua file ke repository GitHub
5. Di Streamlit Sharing, pilih "New App" dan pilih repository Anda
6. Tunggu proses deployment selesai
