import tkinter as tk
import bcrypt
import json
import os
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet

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

    def dashboard(self):
        """Menampilkan dashboard setelah login berhasil."""
        self.dashboard_window = tk.Toplevel(self.root)
        self.dashboard_window.title("Dashboard")
        self.dashboard_window.geometry("400x300")

        ttk.Label(self.dashboard_window, text="Selamat datang di Dashboard!").pack(pady=20)
        exit_btn = ttk.Button(self.dashboard_window, text="Keluar", command=self.keluar_program)
        exit_btn.pack(pady=10)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
