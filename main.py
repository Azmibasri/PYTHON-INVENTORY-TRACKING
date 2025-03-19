import tkinter as tk
import bcrypt
import json
import os
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet

class App:
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

        self.MASTER_HASH = b'$2b$12$97EhEKjGzbWqEMDT11JWCuA0SpPPG5Eumx4rZy7VV9Gd8Sf8QUJTG'

        self.kunci = self.muat_kunci()
        self.cipher = Fernet(self.kunci)
        self.file_data = "kunci.json"
        self.muat_data()

        self.container = ttk.Frame(root)

        # Frame utama untuk login di tengah
        self.formlogin = ttk.Frame(self.container)
        self.label_password = ttk.Label(self.formlogin, text="Password:")
        self.entry_password = ttk.Entry(self.formlogin, show="*")
        self.login_btn = ttk.Button(self.formlogin, text="Login", command=self.cek_password)
        self.Label_buat_akun = ttk.Label(self.container, text="Buat akun baru.")

        self.container.pack(expand=True,fill="both",anchor="center")
        self.formlogin.pack(expand=True,pady=100)
        self.label_password.grid(row=0,column=0,padx=5)
        self.entry_password.grid(row=0,column=1,padx=5)
        self.login_btn.grid(row=1,column=1,pady=5)
        self.Label_buat_akun.pack(side="right")

        self.Label_buat_akun.bind("<Button-1>",lambda event: self.buat_akun_baru())



        self.dashboard_window = None  # Tambahkan variabel untuk melacak dashboard window

    def buat_akun_baru(self):
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.deiconify()  # Jika sudah ada, munculkan kembali
            return

        self.dashboard_window = tk.Toplevel(self.root)  # Hubungkan ke root utama
        self.dashboard_window.title("Buat akun baru")
        self.dashboard_window.geometry("400x300")

        self.container = tk.Frame(self.dashboard_window, bg="red")  # Pastikan ini terkait dengan dashboard_window
        self.formbuatakun = tk.Frame(self.container,bg="blue")
        self.Labelusername = ttk.Label(self.container,text="Usename:")

        self.container.pack(expand=True, fill="both")  # Tambahkan pack agar terlihat
        self.formbuatakun.pack()
        self.Labelusername.grid(row=0,column=0)


        # Lingkungan desain UI

        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.keluar_program)
    

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

    def cek_password(self):
        password = self.entry_password.get().encode()
        if bcrypt.checkpw(password, self.MASTER_HASH):
            messagebox.showinfo("Login Berhasil", "Selamat datang!")
            self.root.withdraw()  # Sembunyikan jendela login, bukan destroy
            self.dashboard()
        else:
            messagebox.showerror("Login Gagal", "Password salah! Coba lagi.")

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

    def dashboard(self):
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.deiconify()  # Jika sudah ada, munculkan kembali
            return

        self.dashboard_window = tk.Toplevel()
        self.dashboard_window.title("Dashboard")
        self.dashboard_window.geometry("400x300")

        ttk.Label(self.dashboard_window, text="Selamat datang di Dashboard!").pack(pady=20)

        exit_btn = ttk.Button(self.dashboard_window, text="Keluar", command=self.keluar_program)
        exit_btn.pack(pady=10)

        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.keluar_program)

    def keluar_program(self):
        if self.dashboard_window:
            self.dashboard_window.destroy()
        self.root.destroy()  # Pastikan aplikasi benar-benar berhenti


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
