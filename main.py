import tkinter as tk
import bcrypt
import json
import os
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
from PIL import Image,ImageTk
import barcode
from barcode.writer import ImageWriter
import csv
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import os
class App:
    MASTER_PASSWORD = b'$2b$12$97EhEKjGzbWqEMDT11JWCuA0SpPPG5Eumx4rZy7VV9Gd8Sf8QUJTG' # Hash dari "Kurik"

    def __init__(self, root):
        self.root = root
        self.lebar_layar = root.winfo_screenwidth()
        self.tinggi_layar = root.winfo_screenheight()
        self.lebar_jendela = 400
        self.tinggi_jendela = 300
        self.posisi_x = (self.lebar_layar - self.lebar_jendela) // 2
        self.posisi_y = (self.tinggi_layar - self.tinggi_jendela) // 2

        self.root.title("Inventory Tracking")
        self.root.geometry(f"{self.lebar_jendela}x{self.tinggi_jendela}+{self.posisi_x}+{self.posisi_y}")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        self.kunci = self.muat_kunci()
        self.cipher = Fernet(self.kunci)
        self.file_data = "data.json"
        self.muat_data()

        self.dashboard_window = None
        self.tampilkan_login()

    def tampilkan_login(self):
        """Menampilkan halaman login."""
        if hasattr(self, "container"):
            self.container.destroy()

        self.container = ttk.Frame(self.root)
        self.container.pack(expand=True, fill="both")

        self.formlogin = ttk.Frame(self.container)
        ttk.Label(self.formlogin, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_email = ttk.Entry(self.formlogin)
        self.entry_email.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.formlogin, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_password = ttk.Entry(self.formlogin, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        self.login_btn = ttk.Button(self.formlogin, text="Login", command=self.cek_password)
        self.login_btn.grid(row=2, column=1, pady=10)

        self.Label_buat_akun = ttk.Label(self.container, text="Buat akun baru.", foreground="blue", cursor="hand2")
        self.Label_buat_akun.pack(side="right", padx=10, pady=10)
        self.Label_buat_akun.bind("<Button-1>", lambda event: self.tampilkan_master_password())

        self.formlogin.pack(pady=50)

    def tampilkan_master_password(self):
        """Meminta Master Password sebelum membuat akun."""
        if hasattr(self, "container"):
            self.container.destroy()

        self.container = ttk.Frame(self.root)
        self.container.pack(expand=True, fill="both")

        self.form_master = ttk.Frame(self.container)
        ttk.Label(self.form_master, text="Masukkan Master Password:").pack(pady=5)
        self.entry_master = ttk.Entry(self.form_master, show="*")
        self.entry_master.pack(pady=5)

        self.btn_master = ttk.Button(self.form_master, text="Verifikasi", command=self.verifikasi_master_password)
        self.btn_master.pack(pady=10)

        self.btn_kembali = ttk.Button(self.container, text="Kembali", command=self.tampilkan_login)
        self.btn_kembali.pack(side="bottom", pady=10)

        self.form_master.pack(pady=50)

    def verifikasi_master_password(self):
        """Memeriksa Master Password sebelum mengizinkan pembuatan akun baru."""
        master_input = self.entry_master.get().encode()
        if bcrypt.checkpw(master_input, self.MASTER_PASSWORD):
            messagebox.showinfo("Sukses", "Master Password benar!")
            self.buat_akun_baru()  # Pindah ke form pendaftaran
        else:
            messagebox.showerror("Error", "Master Password salah!")

    def buat_akun_baru(self):
        """Menampilkan halaman pembuatan akun baru setelah verifikasi Master Password."""
        self.container.destroy()

        self.container = ttk.Frame(self.root)
        self.container.pack(expand=True, fill="both")

        self.form_buat_akun = ttk.Frame(self.container)
        ttk.Label(self.form_buat_akun, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_email_reg = ttk.Entry(self.form_buat_akun)
        self.entry_email_reg.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.form_buat_akun, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_password_reg = ttk.Entry(self.form_buat_akun, show="*")
        self.entry_password_reg.grid(row=1, column=1, padx=5, pady=5)

        self.btn_register = ttk.Button(self.form_buat_akun, text="Daftar", command=self.simpan_akun)
        self.btn_register.grid(row=2, column=1, pady=10)

        self.btn_kembali = ttk.Button(self.container, text="Kembali", command=self.tampilkan_login)
        self.btn_kembali.pack(side="bottom", pady=10)

        self.form_buat_akun.pack(pady=50)

    def simpan_akun(self):
        """Menyimpan akun baru setelah pendaftaran."""
        email = self.entry_email_reg.get()
        password = self.entry_password_reg.get()

        if not email or not password:
            messagebox.showerror("Error", "Email dan Password tidak boleh kosong!")
            return

        for akun in self.data:
            if akun["email"] == email:
                messagebox.showerror("Error", "Email sudah terdaftar!")
                return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        akun_baru = {"email": email, "password": hashed_password.decode()}
        self.data.append(akun_baru)
        self.simpan_data()

        messagebox.showinfo("Sukses", "Akun berhasil dibuat! Silakan login.")
        self.tampilkan_login()

    def cek_password(self):
        """Memeriksa email dan password yang dimasukkan saat login."""
        email = self.entry_email.get()
        password = self.entry_password.get().encode()

        for akun in self.data:
            if akun["email"] == email and bcrypt.checkpw(password, akun["password"].encode()):
                messagebox.showinfo("Login Berhasil", "Selamat datang!")
                self.root.withdraw()
                self.dashboard()
                return

        messagebox.showerror("Login Gagal", "Email atau Password salah!")

    def muat_kunci(self):
        file_kunci = "kunci.key"
        if os.path.exists(file_kunci):
            with open(file_kunci, "rb") as file:
                return file.read()
        else:
            kunci = Fernet.generate_key()
            with open(file_kunci, "wb") as file:
                file.write(kunci)
            return kunci

    def muat_data(self):
        if not os.path.exists(self.file_data):
            self.data = []
            return

        try:
            with open(self.file_data, "rb") as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self.data = json.loads(decrypted_data)
        except:
            self.data = []

    def simpan_data(self):
        data_enkripsi = self.cipher.encrypt(json.dumps(self.data).encode())
        with open(self.file_data, "wb") as file:
            file.write(data_enkripsi)

    def keluar_program(self):
        self.root.destroy()

    def dashboard(self):
        """Menampilkan dashboard setelah login berhasil."""
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.deiconify()  # Jika sudah ada, munculkan kembali
            return

        self.dashboard_window = tk.Toplevel(self.root)
        self.dashboard_window.title("Dashboard")
        self.dashboard_window.resizable(False,False)

        # Ambil ukuran layar dari root, bukan dari self.dashboard_window
        self.lebar_layar = self.root.winfo_screenwidth()
        self.tinggi_layar = self.root.winfo_screenheight()

        self.dashboard_window.geometry(f"{self.lebar_layar}x{self.tinggi_layar}")

        #Ruang UI
        self.container = tk.Frame(self.dashboard_window,bg="blue")
        self.navigasi = tk.Frame(self.container,bg="yellow")
        self.konten = tk.Frame(self.container,bg="red")

        #Navigasi
        self.plus = Image.open("icons/plus.png").convert("RGBA").resize((40, 40))
        self.Plus_image = ImageTk.PhotoImage(self.plus)
        self.tambah_data = ttk.Label(self.navigasi,image=self.Plus_image)

        self.home = Image.open("icons/home.png").convert("RGBA").resize((40, 40))
        self.home_image = ImageTk.PhotoImage(self.home)
        self.grafik = ttk.Label(self.navigasi,image=self.home_image)

        self.ubah = Image.open("icons/edit.png").convert("RGBA").resize((40, 40))
        self.ubah_image = ImageTk.PhotoImage(self.ubah)
        self.manual = ttk.Label(self.navigasi,image=self.ubah_image)

        #Navigasi placement
        self.tambah_data.grid(row=1,column=1,padx=20,pady=10)
        self.grafik.grid(row=0,column=1,padx=20,pady=10)

        self.navigasi.place(x=0,y=0,width=100,height=self.tinggi_layar)
        self.konten.place(x=100,y=0,width=(self.lebar_layar-100),height=self.tinggi_layar)
        self.container.pack(expand=True,fill="both",side="left")

        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.keluar_program)

        #kontrol input
        self.tambah_data.bind("<Button-1>", lambda event: self.tampilkan_tambah_data())
        self.grafik.bind("<Button-1>", lambda event: self.tampilkan_grafik())


    def tampilkan_tambah_data(self):
        # Hapus semua widget yang ada di dalam self.konten
        for widget in self.konten.winfo_children():
            widget.destroy()

        # Tambahkan widget baru
        self.container = tk.Frame(self.konten, bg="white")
        self.menu_scan = tk.Frame(self.container, bg="gray")
        self.preview_scan = tk.Frame(self.container, bg="purple")
        self.preview_data = tk.Frame(self.container, bg="#f12345")

        # Load gambar
        self.scan_bar_img = Image.open("icons/picture.png").convert("RGBA").resize((40, 40))
        self.scan_bar_img = ImageTk.PhotoImage(self.scan_bar_img)

        self.camera_bar_img = Image.open("icons/camera.png").convert("RGBA").resize((40, 40))
        self.camera_bar_img = ImageTk.PhotoImage(self.camera_bar_img)

        self.edit_data_img = Image.open("icons/edit.png").convert("RGBA").resize((40, 40))
        self.edit_data_img = ImageTk.PhotoImage(self.edit_data_img)

        # Tambahkan label dengan gambar
        self.scan_bar = ttk.Label(self.menu_scan, image=self.scan_bar_img)
        self.scan_bar.pack(expand=True,fill="x",side="left",padx=5)

        self.camera_bar = ttk.Label(self.menu_scan, image=self.camera_bar_img)
        self.camera_bar.pack(expand=True,fill="x",side="left",padx=5)

        self.edit_data = ttk.Label(self.menu_scan, image=self.edit_data_img)
        self.edit_data.pack(expand=True,fill="x",side="left",padx=5)

        # Tempatkan frame
        self.container.pack(expand=True, fill="both")
        
        lebar_menu = max(200, self.lebar_layar - 1000)  
        lebar_preview = max(200, self.lebar_layar - 500)  
        
        self.menu_scan.place(x=0, y=0, width=lebar_menu, height=100)
        self.preview_scan.place(x=0, y=100, width=lebar_menu, height=(self.tinggi_layar - 100))
        self.preview_data.place(x=lebar_menu, y=0, width=lebar_preview, height=self.tinggi_layar)

        self.scan_bar.bind("<Button-1>", lambda event: self.tampilkan_scan_bar_img())



    def tampilkan_scan_bar_img(self):
        # Hapus semua widget yang ada di dalam self.konten
        for widget in self.konten.winfo_children():
            widget.destroy()

        self.barang = [
            {"id": "1234567890", "nama": "Laptop XYZ", "harga": 7500000, "tanggal_produksi": "2025-03-20", "produsen": "Tech Company"},
            {"id": "9876543210", "nama": "Smartphone ABC", "harga": 5000000, "tanggal_produksi": "2025-02-15", "produsen": "Mobile Corp"}
        ]

        self.csv_filename = "data_barang.csv"
        with open(self.csv_filename, mode="w", newline="") as file:
            fieldnames = ["id", "nama", "harga", "tanggal_produksi", "produsen"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.barang)

        print(f"✅ Data barang berhasil disimpan dalam '{self.csv_filename}'")

        # ==========================
        # 3. Membaca dan Mendekode Barcode
        # ==========================
        if not hasattr(self, "barcode_filename") or not os.path.exists(self.barcode_filename):
            print("❌ File barcode tidak ditemukan!")
            return

        # Baca database barang dari CSV dengan memastikan kolom "id" dibaca sebagai string
        df = pd.read_csv(self.csv_filename, dtype={"id": str})

        # Buka gambar barcode
        image = cv2.imread(self.barcode_filename)

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

            # Tampilkan gambar hanya jika GUI tersedia
            if cv2.waitKey(1) != -1:  
                cv2.imshow("Barcode Scanner", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            

    def tampilkan_grafik(self):
        # Hapus semua widget yang ada di dalam self.konten
        for widget in self.konten.winfo_children():
            widget.destroy()

        # Tambahkan widget baru
        self.labell = ttk.Label(self.konten, text="Percobaan kedua")
        self.labell.pack()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
