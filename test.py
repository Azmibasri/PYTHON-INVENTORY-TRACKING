import barcode
from barcode.writer import ImageWriter
import csv
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import os

# ==========================
# 1. Membuat Barcode
# ==========================
id_barang = "9876543210"  # ID unik barang

# Pilih tipe barcode (Code128)
barcode_type = barcode.get_barcode_class('code128')

# Buat barcode dan simpan sebagai gambar PNG
barcode_filename = "barang_barcode.png"
my_barcode = barcode_type(id_barang, writer=ImageWriter())
my_barcode.save("barang_barcode")

print(f"✅ Barcode berhasil dibuat dan disimpan sebagai '{barcode_filename}'")

# ==========================
# 2. Menyimpan Data Barang ke CSV
# ==========================
barang = [
    {"id": "1234567890", "nama": "Laptop XYZ", "harga": 7500000, "tanggal_produksi": "2025-03-20", "produsen": "Tech Company"},
    {"id": "9876543210", "nama": "Smartphone ABC", "harga": 5000000, "tanggal_produksi": "2025-02-15", "produsen": "Mobile Corp"}
]

csv_filename = "data_barang.csv"
with open(csv_filename, mode="w", newline="") as file:
    fieldnames = ["id", "nama", "harga", "tanggal_produksi", "produsen"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(barang)

print(f"✅ Data barang berhasil disimpan dalam '{csv_filename}'")

# ==========================
# 3. Membaca dan Mendekode Barcode
# ==========================
# Periksa apakah file barcode ada
if not os.path.exists(barcode_filename):
    print("❌ File barcode tidak ditemukan!")
else:
    # Baca database barang dari CSV dengan memastikan kolom "id" dibaca sebagai string
    df = pd.read_csv(csv_filename, dtype={"id": str})

    # Buka gambar barcode
    image = cv2.imread(barcode_filename)

    # Konversi ke grayscale (opsional, bisa membantu pembacaan)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Decode barcode
    barcodes = decode(gray)

    if not barcodes:
        print("❌ Tidak ada barcode yang terdeteksi!")
    else:
        for barcode in barcodes:
            id_barang = barcode.data.decode("utf-8")
            print(f"🔍 ID Barang Terbaca: {id_barang}")

            # Cari data barang berdasarkan ID
            data_barang = df[df["id"] == id_barang]
            if not data_barang.empty:
                print("✅ Data Barang Ditemukan:")
                print(data_barang.to_string(index=False))
            else:
                print("❌ Barang tidak ditemukan di database!")

        cv2.waitKey(0)
        cv2.destroyAllWindows()

