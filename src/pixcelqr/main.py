# src/pixcelqr/main.py

import tkinter as tk
from PIL import ImageTk
from generator import QArtGenerator

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("PixcelQR Generator")

        self.box_size = 15
        self.border = 4

        self.qart = QArtGenerator("https://github.com/YuzukiYukariProject")
        
        self.create_widgets()
        self.update_canvas()

    def create_widgets(self):
        image_width = (self.qart.size + self.border * 2) * self.box_size
        image_height = (self.qart.size + self.border * 2) * self.box_size

        self.canvas = tk.Canvas(self.master, width=image_width, height=image_height)
        self.canvas.pack()
        
        # <Button-1>は左クリックを意味します
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def update_canvas(self):
        """キャンバスの画像を現在のQRコードの状態に更新する"""
        self.qr_image_pil = self.qart.generate_image(box_size=self.box_size, border=self.border)
        self.qr_image_tk = ImageTk.PhotoImage(self.qr_image_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.qr_image_tk)

    def on_canvas_click(self, event):
        """キャンバスがクリックされたときに呼び出される関数"""
        # クリックされたピクセル座標から、QRコードのドット座標に変換
        border_pixels = self.border * self.box_size
        col = (event.x - border_pixels) // self.box_size
        row = (event.y - border_pixels) // self.box_size
        
        # ドットの色を反転させる
        success = self.qart.flip_dot(row, col)
        
        if success:
            # 変更が成功した場合のみ、キャンバスを再描画
            self.update_canvas()
            # 読み取り可能かチェックして、ウィンドウのタイトルに表示
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
