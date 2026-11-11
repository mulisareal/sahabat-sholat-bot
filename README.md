# SahabatSholat: Panduan & Fiqih Sholat Sehari-hari

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0-emerald.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-passing.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**SahabatSholat** adalah aplikasi chatbot berbasis web (*rule-based*) yang dirancang khusus untuk menjawab pertanyaan seputar ibadah sholat fardhu dan sunnah, syarat sah, rukun, tata cara, hingga penanganan kondisi khusus seperti sholat jamak-qashar dan sujud sahwi.

Chatbot ini dibangun menggunakan **Flask** di sisi backend dan memanfaatkan gabungan algoritma pemrosesan bahasa alami (**NLP**) sederhana untuk mencocokkan niat (*intent*) pengguna secara presisi.

---

## Fitur Utama

- 🎯 **Pencocokan Intent Hybrid (NLU Engine)**: Menggabungkan 3 metrik penilaian: *Jaccard Similarity* (40%), *Fuzzy Character Matching* (30%), dan *Pattern Coverage* (30%).
- 📖 **11 Intent Berbasis Fiqih**: Menjawab topik dasar (salam, identitas, rukun, syarat sah, niat, tata cara) hingga kondisi praktis (jamak-qashar musafir & sujud sahwi).
- 🔤 **Praproses & Normalisasi Teks**: Dilengkapi penanganan *case folding*, *cleaning*, pembuangan kata hubung (*stopword removal*), dan normalisasi kata tidak baku/singkatan.
- 💬 **Antarmuka Chat Asynchronous**: Dibangun dengan JavaScript `fetch()` API untuk komunikasi *real-time* tanpa memuat ulang halaman.
- 🎓 **Mode Belajar (Inspection Mode)**: Fitur untuk melihat skor kemiripan dan kandidat intent yang lolos ambang batas secara langsung di antarmuka chat.
- 📊 **Panel Statistik & Evaluasi Admin**: Menampilkan metrik penggunaan, persentase pertanyaan terdeteksi, dan daftar pertanyaan yang belum dikenali.
- 🗄️ **Penyimpanan Sesi Persistent**: Menyimpan riwayat percakapan per sesi pengguna ke database SQLite.

---

## Arsitektur Mesin NLP (Engine v2)

Setiap pesan pengguna diproses melalui formula skor berbobot berikut:

$$\text{Skor Akhir} = 0.4 \times \text{Jaccard} + 0.3 \times \text{Fuzzy} + 0.3 \times \text{Cakupan}$$

- **Jaccard Similarity**: Mengukur rasio kesamaan token kata antara input dan pola JSON.
- **Fuzzy Matching (`difflib`)**: Menangani kesalahan ketik (*typo*) pada kata.
- **Cakupan (Coverage)**: Memastikan kata kunci utama dalam pola terpenuhi.
- **Ambang Batas Default**: `0.45` (input di bawah ambang batas akan memicu pesan *fallback*).

---

## Struktur Proyek

```text
chatbot-sholat/
├── themes/
│   └── sholat.json          # Basis pengetahuan intent & pola jawaban
├── chatbot/
│   ├── __init__.py
│   ├── engine.py            # Logika NLP, praproses, & algoritma similarity
│   └── database.py          # Modul SQLite untuk menyimpan riwayat chat
├── templates/               # Template HTML Jinja2 (base, index, chat, admin, 404)
├── static/                  # Berkas statis (CSS styling & JavaScript fetch)
├── evaluasi/
│   └── sholat.csv           # Dataset uji untuk pengujian akurasi
├── tests/
│   └── test_engine.py       # Pengujian unit otomatis via Pytest
├── app.py                   # Aplikasi utama Flask & REST API
├── cli.py                   # Antarmuka obrolan mode terminal
├── evaluate.py              # Skrip evaluasi akurasi & eksperimen ambang batas
└── requirements.txt         # Daftar pustaka dependensi
