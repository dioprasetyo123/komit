import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="manajemen_tugas"
    )


class Tugas:
    def __init__(self, id, mata_kuliah, deskripsi, deadline, selesai):
        self.id = id
        self.mata_kuliah = mata_kuliah
        self.deskripsi = deskripsi
        self.deadline = deadline
        self.selesai = selesai

class AplikasiManajemenTugas:
    def __init__(self, root):
        self.root = root
        self.root.title("jangan lupa tugas")
        self.root.geometry("800x450")

        self.daftar_tugas = []
        self.editing_id = None  # Untuk menyimpan ID tugas yang sedang diedit

        self.setup_ui()
        self.load_tugas()

    def setup_ui(self):
        # Frame input data
        frame_input = tk.Frame(self.root)
        frame_input.pack(pady=10)

        tk.Label(frame_input, text="Mata Kuliah").grid(row=0, column=0)
        tk.Label(frame_input, text="Deskripsi").grid(row=0, column=1)
        tk.Label(frame_input, text="Deadline (YYYY-MM-DD)").grid(row=0, column=2)

        self.entry_mk = tk.Entry(frame_input, width=20)
        self.entry_deskripsi = tk.Entry(frame_input, width=60)
        self.entry_deadline = tk.Entry(frame_input, width=15)

        self.entry_mk.grid(row=1, column=0, padx=5)
        self.entry_deskripsi.grid(row=1, column=1, padx=5)
        self.entry_deadline.grid(row=1, column=2, padx=5)

        self.btn_submit = tk.Button(frame_input, text="Tambah Tugas", command=self.tambah_tugas)
        self.btn_submit.grid(row=1, column=3, padx=5)

        # Tabel tugas
        self.tree = ttk.Treeview(
            self.root,
            columns=("Mata Kuliah", "Deskripsi", "Deadline", "Status"),
            show="headings"
        )
        self.tree.heading("Mata Kuliah", text="Mata Kuliah")
        self.tree.heading("Deskripsi", text="Deskripsi")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill="both", expand=True, pady=10)

        # Frame tombol aksi
        frame_button = tk.Frame(self.root)
        frame_button.pack(pady=5)

        tk.Button(frame_button, text="Tandai Selesai", command=self.tandai_selesai).pack(side="left", padx=10)
        tk.Button(frame_button, text="Hapus Tugas", command=self.hapus_tugas).pack(side="left", padx=10)
        tk.Button(frame_button, text="Edit Tugas", command=self.edit_tugas).pack(side="left", padx=10)

    def tambah_tugas(self):
        mk = self.entry_mk.get()
        deskripsi = self.entry_deskripsi.get()
        deadline = self.entry_deadline.get()

        if not (mk and deskripsi and deadline):
            messagebox.showwarning("LENGKAPI SEMUA KOLOM", "HARAP ISI SEMUA KOLOM, CUKUP HATIMU SAJA YANG KOSONG.")
            return

        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Tanggal Salah", "Gunakan format YYYY-MM-DD.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tugas (mata_kuliah, deskripsi, deadline) VALUES (%s, %s, %s)",
                (mk, deskripsi, deadline)
            )
            conn.commit()
            conn.close()
            self.load_tugas()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menambahkan tugas: {e}")

    def load_tugas(self):
        self.daftar_tugas.clear()
        self.tree.delete(*self.tree.get_children())
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, mata_kuliah, deskripsi, deadline, selesai FROM tugas")
            for row in cursor.fetchall():
                id, mk, desk, ddl, selesai = row
                tugas = Tugas(id, mk, desk, ddl.strftime("%Y-%m-%d"), selesai)
                self.daftar_tugas.append(tugas)
                status = "Selesai" if tugas.selesai else "Belum"
                self.tree.insert("", "end", values=(mk, desk, ddl.strftime("%Y-%m-%d"), status))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data: {e}")

    def tandai_selesai(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Pilih Tugas", "Pilih tugas yang ingin ditandai selesai.")
            return
        index = self.tree.index(selected[0])
        tugas = self.daftar_tugas[index]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE tugas SET selesai = 1 WHERE id = %s", (tugas.id,))
            conn.commit()
            conn.close()
            self.load_tugas()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memperbarui status tugas: {e}")

    def hapus_tugas(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Pilih Tugas", "Pilih tugas yang ingin dihapus.")
            return
        index = self.tree.index(selected[0])
        tugas = self.daftar_tugas[index]

        confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus tugas: {tugas.mata_kuliah}?")
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tugas WHERE id = %s", (tugas.id,))
            conn.commit()
            conn.close()
            self.load_tugas()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus tugas: {e}")

    def edit_tugas(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Pilih Tugas", "Pilih tugas yang ingin diedit.")
            return
        index = self.tree.index(selected[0])
        tugas = self.daftar_tugas[index]

        self.entry_mk.delete(0, tk.END)
        self.entry_deskripsi.delete(0, tk.END)
        self.entry_deadline.delete(0, tk.END)

        self.entry_mk.insert(0, tugas.mata_kuliah)
        self.entry_deskripsi.insert(0, tugas.deskripsi)
        self.entry_deadline.insert(0, tugas.deadline)

        self.editing_id = tugas.id
        self.btn_submit.config(text="Simpan Perubahan", command=self.simpan_perubahan)

    def simpan_perubahan(self):
        mk = self.entry_mk.get()
        deskripsi = self.entry_deskripsi.get()
        deadline = self.entry_deadline.get()

        if not (mk and deskripsi and deadline):
            messagebox.showwarning("Peringatan", "Harap isi semua kolom.")
            return

        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Tanggal Salah", "Gunakan format YYYY-MM-DD.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tugas SET mata_kuliah = %s, deskripsi = %s, deadline = %s WHERE id = %s",
                (mk, deskripsi, deadline, self.editing_id)
            )
            conn.commit()
            conn.close()
            self.load_tugas()
            self.clear_form()
            self.editing_id = None
            self.btn_submit.config(text="Tambah Tugas", command=self.tambah_tugas)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan perubahan: {e}")

    def clear_form(self):
        self.entry_mk.delete(0, tk.END)
        self.entry_deskripsi.delete(0, tk.END)
        self.entry_deadline.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiManajemenTugas(root)
    root.mainloop()
