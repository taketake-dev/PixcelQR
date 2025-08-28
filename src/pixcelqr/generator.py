# src/pixcelqr/generator.py

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

# (ALIGNMENT_PATTERN_COORDS の長いリストは前回と同じなので、ここでは省略します)
ALIGNMENT_PATTERN_COORDS = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
    8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50], 11: [6, 30, 54], 12: [6, 32, 58],
    13: [6, 34, 62], 14: [6, 26, 46, 66], 15: [6, 26, 48, 70], 16: [6, 26, 50, 74],
    17: [6, 30, 54, 78], 18: [6, 30, 56, 82], 19: [6, 30, 58, 86], 20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94], 22: [6, 26, 50, 74, 98], 23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106], 25: [6, 32, 58, 84, 110], 26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118], 28: [6, 26, 50, 74, 98, 122], 29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130], 31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138], 33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146], 35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154], 37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162], 39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
}

class QArtGenerator:
    def __init__(self, data, error_correction=qrcode.constants.ERROR_CORRECT_H):
        self.data = data
        self.error_correction = error_correction
        self._generate()

    def update_data(self, new_data):
        """
        新しいデータでQRコードの内部情報を再生成するメソッド
        """
        self.data = new_data
        self._generate()

    def _generate(self):
        qr = qrcode.QRCode(error_correction=self.error_correction)
        qr.add_data(self.data)
        qr.make(fit=True)
        
        self.matrix = qr.modules
        self.version = qr.version
        self.size = qr.modules_count
        self.safe_area_map = self._create_safe_area_map()

    def _create_safe_area_map(self):
        mask = [[0] * self.size for _ in range(self.size)]
        
        # ファインダーパターンとセパレータ
        for y_start in (0, self.size - 8):
            for x_start in (0, self.size - 8):
                if y_start > 0 and x_start > 0: continue
                for r in range(8):
                    for c in range(8):
                        mask[y_start + r][x_start + c] = 4 if r == 7 or c == 7 else 1
        
        # タイミングパターン
        for i in range(8, self.size - 8):
            mask[6][i] = 3
            mask[i][6] = 3

        # アライメントパターン
        if self.version > 1 and self.version in ALIGNMENT_PATTERN_COORDS:
            coords = ALIGNMENT_PATTERN_COORDS[self.version]
            for y_center in coords:
                for x_center in coords:
                    is_near_finder = (y_center < 9 and x_center < 9) or \
                                     (y_center < 9 and x_center > self.size - 9) or \
                                     (y_center > self.size - 9 and x_center < 9)
                    if is_near_finder: continue
                    for r in range(-2, 3):
                        for c in range(-2, 3):
                            mask[y_center + r][x_center + c] = 2
        return mask

    def flip_dot(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            if self.safe_area_map[row][col] == 0:
                self.matrix[row][col] = not self.matrix[row][col]
                return True
        return False

    def generate_image(self, box_size=10, border=4):
        image_size = (self.size + border * 2) * box_size
        img = Image.new("L", (image_size, image_size), "white")
        draw_context = img.load()

        for r, row_data in enumerate(self.matrix):
            for c, is_black in enumerate(row_data):
                if is_black:
                    x_start = (c + border) * box_size
                    y_start = (r + border) * box_size
                    for i in range(box_size):
                        for j in range(box_size):
                            draw_context[x_start + i, y_start + j] = 0
        return img

    def is_readable(self):
        img = self.generate_image()
        decoded = decode(img)
        if decoded:
            return decoded[0].data.decode("utf-8") == self.data
        return False
