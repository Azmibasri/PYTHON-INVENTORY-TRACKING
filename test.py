import cv2
import sqlite3
import pandas as pd
import tkinter as tk
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk

class BarcodeScanner:
    def __init__(self, proses, label, hasil_label, preview_scan):
        self.proses = proses
        self.label = label
        self.hasil_label = hasil_label
        self.preview_scan = preview_scan
        self.cap = cv2.VideoCapture(0)
        self.last_barcode = None
        self.db_filename = "data_barang.db"
        self.init_database()
        self.scan_barcode()

    def init_database(self):
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id TEXT PRIMARY KEY,
                nama TEXT,
                harga INTEGER,
                tanggal_produksi TEXT,
                produsen TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode_id TEXT,
                nama TEXT,
                harga INTEGER,
                tanggal_produksi TEXT,
                produsen TEXT,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
        self.barang = [
            ("1234567890", "Laptop XYZ", 7500000, "2025-03-20", "Tech Company"),
            ("9876543210", "Smartphone ABC", 5000000, "2025-02-15", "Mobile Corp"),
            ("7484478871", "LOQ Laptop", 13000000, "2025-02-15", "Lenovo")
        ]
        self.cursor.executemany("""
            INSERT OR IGNORE INTO barang (id, nama, harga, tanggal_produksi, produsen)
            VALUES (?, ?, ?, ?, ?)
        """, self.barang)
        self.conn.commit()
    
    def scan_barcode(self):
        ret, frame = self.cap.read()
        if not ret:
            self.proses.after(10, self.scan_barcode)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)
        detected_barcodes = []

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            detected_barcodes.append(barcode_data)
            
            if barcode_data == self.last_barcode:
                continue  # Abaikan jika barcode yang sama masih terlihat

            self.last_barcode = barcode_data
            barcode_type = barcode.type
            x, y, w, h = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = f"{barcode_data} ({barcode_type})"
            self.hasil_label.config(text=text)
            
            self.cursor.execute("SELECT * FROM barang WHERE id = ?", (barcode_data,))
            data_barang = self.cursor.fetchall()
            
            for widget in self.preview_scan.winfo_children():
                widget.destroy()

            if data_barang:
                tk.Label(self.preview_scan, text="Data Barang ditemukan:").pack()
                for row in data_barang:
                    tk.Label(self.preview_scan, text=f"ID: {row[0]}, Nama: {row[1]}, Harga: {row[2]}, Tanggal: {row[3]}, Produsen: {row[4]}").pack()
                    
                    # Simpan data ke tabel log
                    self.cursor.execute("""
                        INSERT INTO log (barcode_id, nama, harga, tanggal_produksi, produsen)
                        VALUES (?, ?, ?, ?, ?)
                    """, (row[0], row[1], row[2], row[3], row[4]))
                    self.conn.commit()
            else:
                tk.Label(self.preview_scan, text="Barang tidak ditemukan di database").pack()

        if not detected_barcodes:
            self.last_barcode = None
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.label.imgtk = imgtk
        self.label.config(image=imgtk)
    
        self.proses.after(10, self.scan_barcode)
    
    def on_close(self):
        self.cap.release()
        self.conn.close()
        self.proses.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Barcode Scanner")
    
    label = tk.Label(root)
    label.pack()
    hasil_label = tk.Label(root, text="Hasil Scan:")
    hasil_label.pack()
    preview_scan = tk.Frame(root)
    preview_scan.pack()
    
    scanner = BarcodeScanner(root, label, hasil_label, preview_scan)
    root.protocol("WM_DELETE_WINDOW", scanner.on_close)
    root.mainloop()