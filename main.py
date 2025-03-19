import tkinter as tk
import bcrypt
import json
import os 
from tkinter import ttk,messagebox
from cryptography.fernet import Fernet

def muat_kunci():
    file_kunci = "kunci.key"
    if os.path.exists(file_kunci):
        with open(file_kunci,"rb") as file:
            return file.read()
    else:
        kunci = Fernet.generate_key()
        with open(file_kunci,"wb") as file:
            file.write(kunci)
        return kunci

def cek_password():
    password = KotakPassword.get().encode()
    if bcrypt.checkpw(password,MASTER_HASH):
        messagebox.showinfo("Login Berhasil", "Selamat datang!")
        root.withdraw()
        root.utama()
    else:
        messagebox.showerror("Login Gagal?","Password salah! Coba lagi.")

def muat_data(DATA_FILE):
    if not os.path.exists(DATA_FILE):
        data = []
        return
    
    try:
        with open(DATA_FILE, "rb") as file:
            encrypted_data = file.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data)
    except:
        data = []
def simpan_data(data):
    data_enkripsi = cipher.encrypt(json.dumps(data).encode())
    with open(file_data,"wb") as file:
        file.write(data_enkripsi)

root = tk.Tk()

lebar_layar = root.winfo_screenwidth()
tinggi_layar = root.winfo_screenmmheight()

lebar_jendela = 400
tinggi_jendela = 300

posisi_x = (lebar_layar - lebar_jendela) // 2
posisi_y = (tinggi_layar - tinggi_jendela) // 2

root.title("Inventory Tracking")
root.geometry(f"{lebar_jendela}x{tinggi_jendela}+{posisi_x}+{posisi_y+300}")
root.overrideredirect(True)
root.resizable(False,False)

MASTER_HASH = b'$2b$12$97EhEKjGzbWqEMDT11JWCuA0SpPPG5Eumx4rZy7VV9Gd8Sf8QUJTG'

kunci = muat_kunci()
cipher = Fernet(kunci)
file_data = "kunci.json"
muat_data(file_data)

KotakUtama = ttk.Frame(root)
KotakUtama.pack(padx=10,pady=60)

ttk.Label(KotakUtama, text="Password:").grid(row=1, column=1, padx=5, pady=5)
KotakPassword = ttk.Entry(KotakUtama, show="*")
KotakPassword.grid(row=1, column=2, padx=5, pady=5)

ttk.Button(KotakUtama, text="Login", command=cek_password).grid(row=2, column=2, pady=10)

def utama():
    utama = tk.Toplevel()
    utama.geometry("500x300")
    utama.mainloop()

root.mainloop()