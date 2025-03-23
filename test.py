import cv2
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner")

        # Label untuk menampilkan video
        self.label = Label(root)
        self.label.pack()

        # Label untuk menampilkan hasil barcode
        self.result_label = Label(root, text="Scan a barcode...", font=("Arial", 14))
        self.result_label.pack()

        # Buka kamera
        self.cap = cv2.VideoCapture(0)

        # Jalankan pemindaian
        self.scan_barcode()

        # Tutup kamera saat jendela ditutup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def scan_barcode(self):
        ret, frame = self.cap.read()
        if ret:
            # Konversi ke grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Decode barcode
            barcodes = decode(gray)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type

                # Gambar kotak di sekitar barcode
                x, y, w, h = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Tampilkan hasil scan
                text = f"{barcode_data} ({barcode_type})"
                self.result_label.config(text=text)

            # Konversi frame ke format Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.label.imgtk = imgtk
            self.label.config(image=imgtk)

        # Looping scan setiap 10ms
        self.root.after(10, self.scan_barcode)

    def on_close(self):
        self.cap.release()
        self.root.destroy()

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeScannerApp(root)
    root.mainloop()
