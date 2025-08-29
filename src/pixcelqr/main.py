# src/pixcelqr/main.py

import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import ImageTk
# URLを解析するためのライブラリをインポートします
from urllib.parse import urlparse
from generator import QArtGenerator

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("PixcelQR Generator")

        self.box_size = 15
        self.border = 4
        self.initial_data = "https://www.ah-soft.com/vocaloid/yukari/"
        self.current_color = "#000000"
        self.draw_mode = tk.StringVar(value="paint")

        self.qart = QArtGenerator(self.initial_data)
        
        self.create_widgets()
        # 起動時に最初のURLをチェックします
        self.validate_and_update_status()
        self.update_canvas()

    def create_widgets(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(control_frame, text="Data:").pack(side=tk.LEFT)
        self.data_entry = tk.Entry(control_frame)
        self.data_entry.insert(0, self.initial_data)
        self.data_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        # 入力があるたびにURL検証関数を呼び出すように設定します
        self.data_entry.bind("<KeyRelease>", self.validate_and_update_status)

        # URLのステータスを表示するためのラベルを新しく追加します
        self.url_status_label = tk.Label(control_frame, text="", font=("Helvetica", 10))
        self.url_status_label.pack(side=tk.LEFT, padx=(0, 10))

        self.generate_button = tk.Button(control_frame, text="Generate", command=self.generate_qr)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.color_button = tk.Button(control_frame, text="Color", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=(0, 2))
        self.color_preview = tk.Label(control_frame, text="  ", bg=self.current_color, relief="sunken")
        self.color_preview.pack(side=tk.LEFT, padx=(0, 10))

        mode_frame = tk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Paint", variable=self.draw_mode, value="paint").pack(anchor=tk.W)
        tk.Radiobutton(mode_frame, text="Erase", variable=self.draw_mode, value="erase").pack(anchor=tk.W)

        self.save_button = tk.Button(control_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.RIGHT)

        image_width = (self.qart.size + self.border * 2) * self.box_size
        image_height = (self.qart.size + self.border * 2) * self.box_size
        self.canvas = tk.Canvas(self.master, width=image_width, height=image_height, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def update_canvas(self):
        # (このメソッドの中身は変更ありません)
        new_width = (self.qart.size + self.border * 2) * self.box_size
        new_height = (self.qart.size + self.border * 2) * self.box_size
        self.canvas.config(width=new_width, height=new_height)
        
        self.qr_image_pil = self.qart.generate_image(
            box_size=self.box_size, border=self.border
        )
        self.qr_image_tk = ImageTk.PhotoImage(self.qr_image_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.qr_image_tk)
        self.check_readability()

    def on_canvas_click(self, event):
        # (このメソッドの中身は変更ありません)
        border_pixels = self.border * self.box_size
        col = (event.x - border_pixels) // self.box_size
        row = (event.y - border_pixels) // self.box_size
        
        mode = self.draw_mode.get()
        if mode == "paint":
            success = self.qart.paint_dot(row, col, self.current_color)
        elif mode == "erase":
            success = self.qart.erase_dot(row, col)
        else:
            success = False
        
        if success:
            self.update_canvas()

    def generate_qr(self):
        # Generateボタンが押されたときも、念のためステータスを更新します
        self.validate_and_update_status()
        new_data = self.data_entry.get()
        if new_data:
            self.qart.update_data(new_data)
            self.update_canvas()

    def save_image(self):
        # (このメソッドの中身は変更ありません)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save QR Code Art"
        )
        if filepath:
            self.qr_image_pil.save(filepath)
            print(f"Image saved to {filepath}")

    def check_readability(self):
        # (このメソッドの中身は変更ありません)
        if self.qart.is_readable():
            self.master.title("PixcelQR Generator - [Readable]")
        else:
            self.master.title("PixcelQR Generator - [UNREADABLE!]")
            
    def choose_color(self):
        # (このメソッドの中身は変更ありません)
        color_code = colorchooser.askcolor(title="Choose color", initialcolor=self.current_color)
        if color_code and color_code[1]:
            self.current_color = color_code[1]
            self.color_preview.config(bg=self.current_color)

    # --- ここからが新しく追加されたメソッドです ---
    def validate_url(self, url_string):
        """
        文字列が有効なURL形式かチェックする
        """
        try:
            result = urlparse(url_string)
            # scheme (httpなど) と netloc (ドメイン名) の両方が存在すればOKとします
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def validate_and_update_status(self, event=None):
        """
        入力ボックスの文字列を検証し、ステータスラベルを更新する
        """
        text = self.data_entry.get()
        if not text:
            self.url_status_label.config(text="")
            return

        if self.validate_url(text):
            self.url_status_label.config(text="✓ Valid URL", fg="green")
        else:
            self.url_status_label.config(text="✗ Not a valid URL", fg="red")
    # --- ここまで ---

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
