import tkinter as tk
import bcrypt
import json
import os 
from tkinter import ttk,messagebox
from cryptography.fernet import Fernet

class App:
    def __init__(self,root):
        self.root = root

        self.lebar_layar = root.winfo_screenwidth()
        self.tinggi_layar = root.winfo_screenmmheight()

        self.lebar_jendela = 400
        self.tinggi_jendela = 300

        self.posisi_x = (self.lebar_layar - self.lebar_jendela) // 2
        self.posisi_y = (self.tinggi_layar - self.tinggi_jendela) // 2

        self.root.title("Inventory Tracking")
        self.root.geometry(f"{self.lebar_jendela}x{self.tinggi_jendela}+{self.posisi_x}+{self.posisi_y+300}")
        self.root.overrideredirect(True)
        self.root.resizable(False,False)

        self.MASTER_HASH = b'$2b$12$97EhEKjGzbWqEMDT11JWCuA0SpPPG5Eumx4rZy7VV9Gd8Sf8QUJTG'

        
        self.kunci = self.muat_kunci()
        self.cipher = Fernet(self.kunci)
        self.file_data = "kunci.json"
        self.muat_data()

        self.KotakUtama = ttk.Frame(root)
        self.KotakUtama.pack(padx=10,pady=60)

        ttk.Label(self.KotakUtama, text="Password:").grid(row=1, column=1, padx=5, pady=5)
        self.KotakPassword = ttk.Entry(self.KotakUtama, show="*")
        self.KotakPassword.grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(self.KotakUtama, text="Login", command=self.cek_password).grid(row=2, column=2, pady=10)
    
    def muat_kunci(self):
        file_kunci = "kunci.key"
        if os.path.exists(file_kunci):
            with open(file_kunci,"rb") as file:
                return file.read()
        else:
            kunci = Fernet.generate_key()
            with open(file_kunci,"wb") as file:
                file.write(kunci)
            return kunci
    def cek_password(self):
        password = self.KotakPassword.get().encode()
        if bcrypt.checkpw(password,self.MASTER_HASH):
            messagebox.showinfo("Login Berhasil", "Selamat datang!")
            self.root.withdraw()
            self.dashboard()
        else:
            messagebox.showerror("Login Gagal","Password salah! Coba lagi.")

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
        with open(self.file_data,"wb") as file:
            file.write(data_enkripsi)
    
    def dashboard(self):
        self.root = tk.Toplevel(self.root)
        self.root.title("Dashboard")
        self.root.geometry("400x300")
        self.root.mainloop()




if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

