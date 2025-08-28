# src/pixcelqr/main.py

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from generator import QArtGenerator

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("PixcelQR Generator")

        self.box_size = 15
        self.border = 4
        self.initial_data = "https://www.ah-soft.com/vocaloid/yukari/"

        self.qart = QArtGenerator(self.initial_data)
        
        self.create_widgets()
        self.update_canvas()

    def create_widgets(self):
        # --- 操作パネル用のフレームを作成 ---
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # データ入力ボックス
        tk.Label(control_frame, text="Data:").pack(side=tk.LEFT)
        self.data_entry = tk.Entry(control_frame)
        self.data_entry.insert(0, self.initial_data)
        self.data_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # 生成ボタン
        self.generate_button = tk.Button(control_frame, text="Generate", command=self.generate_qr)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # 保存ボタン
        self.save_button = tk.Button(control_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        # --- QRコード表示用のキャンバスを作成 ---
        image_width = (self.qart.size + self.border * 2) * self.box_size
        image_height = (self.qart.size + self.border * 2) * self.box_size
        self.canvas = tk.Canvas(self.master, width=image_width, height=image_height, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def update_canvas(self):
        # キャンバスのサイズを現在のQRコードに合わせて変更
        new_width = (self.qart.size + self.border * 2) * self.box_size
        new_height = (self.qart.size + self.border * 2) * self.box_size
        self.canvas.config(width=new_width, height=new_height)

        self.qr_image_pil = self.qart.generate_image(box_size=self.box_size, border=self.border)
        self.qr_image_tk = ImageTk.PhotoImage(self.qr_image_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.qr_image_tk)
        self.check_readability()

    def on_canvas_click(self, event):
        border_pixels = self.border * self.box_size
        col = (event.x - border_pixels) // self.box_size
        row = (event.y - border_pixels) // self.box_size
        
        if self.qart.flip_dot(row, col):
            self.update_canvas()

    def generate_qr(self):
        """生成ボタンが押されたときの処理"""
        new_data = self.data_entry.get()
        if new_data:
            self.qart.update_data(new_data)
            self.update_canvas()

    def save_image(self):
        """保存ボタンが押されたときの処理"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save QR Code Art"
        )
        if filepath:
            self.qr_image_pil.save(filepath)
            print(f"Image saved to {filepath}")

    def check_readability(self):
        """読み取り可能かチェックしてウィンドウタイトルを更新"""
        if self.qart.is_readable():
            self.master.title("PixcelQR Generator - [Readable]")
        else:
            self.master.title("PixcelQR Generator - [UNREADABLE!]")

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
