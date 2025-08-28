# scripts/05_full_safe_area_map.py

"""
QRコードのバージョン1から40までのを塗りつぶします。
"""

import qrcode
from PIL import Image

# QRコードのバージョン1から40までの、完全なアライメントパターン中心座標データ
# QRコードの国際規格(ISO/IEC 18004)に基づいています
ALIGNMENT_PATTERN_COORDS = {
    1: [], 
    2: [6, 18], 
    3: [6, 22], 
    4: [6, 26], 
    5: [6, 30], 
    6: [6, 34], 
    7: [6, 22, 38],
    8: [6, 24, 42], 
    9: [6, 26, 46], 
    10: [6, 28, 50], 
    11: [6, 30, 54], 
    12: [6, 32, 58],
    13: [6, 34, 62], 
    14: [6, 26, 46, 66], 
    15: [6, 26, 48, 70], 
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78], 
    18: [6, 30, 56, 82], 
    19: [6, 30, 58, 86], 
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94], 
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106], 
    25: [6, 32, 58, 84, 110], 
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118], 
    28: [6, 26, 50, 74, 98, 122], 
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130], 
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138], 
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146], 
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154], 
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162], 
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
}

def get_qr_version(matrix):
    size = len(matrix)
    return (size - 17) // 4

def get_safe_area_map(matrix):
    size = len(matrix)
    version = get_qr_version(matrix)
    print(f"QRコードのバージョン: {version}")
    mask = [[0] * size for _ in range(size)]

    # ファインダーパターンとセパレータ
    for y_start in (0, size - 8):
        for x_start in (0, size - 8):
            if y_start > 0 and x_start > 0: continue
            for r in range(8):
                for c in range(8):
                    mask[y_start + r][x_start + c] = 4 if r == 7 or c == 7 else 1
    
    # タイミングパターン
    for i in range(8, size - 8):
        mask[6][i] = 3
        mask[i][6] = 3

    # アライメントパターン (バージョンに応じた位置)
    if version > 1 and version in ALIGNMENT_PATTERN_COORDS:
        coords = ALIGNMENT_PATTERN_COORDS[version]
        for y_center in coords:
            for x_center in coords:
                is_near_finder = (y_center < 9 and x_center < 9) or \
                                 (y_center < 9 and x_center > size - 9) or \
                                 (y_center > size - 9 and x_center < 9)
                if is_near_finder: continue
                for r in range(-2, 3):
                    for c in range(-2, 3):
                        mask[y_center + r][x_center + c] = 2

    return mask

def main():
    long_data = "This is a very long string to test the QR code generation for higher versions, ensuring that all alignment patterns are correctly identified and mapped. Let's see if it works for version 8 or even higher. The quick brown fox jumps over the lazy dog. 1234567890."
    
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(long_data)
    qr.make(fit=True)
    matrix = qr.modules
    version = get_qr_version(matrix)
    size = len(matrix)
    print(f"データ量に合わせて、バージョン{version} ({size}x{size}マス)のQRコードが生成されました。")

    # --- ステップ1: 元のQRコードを生成して表示 ---
    print("\nまず、元のQRコードを表示します。")
    print("ウィンドウを閉じると、色分けされた地図が表示されます。")
    # qrcode.make() は、データを元に直接画像オブジェクトを生成する便利な関数です
    original_img = qrcode.make(long_data, error_correction=qrcode.constants.ERROR_CORRECT_H)
    original_img.show()
    original_img.save("qr_original_large.png")


    # --- ステップ2: 聖域の地図を生成して表示 ---
    safe_area_map = get_safe_area_map(matrix)
    
    box_size = 10
    map_img = Image.new("RGB", (size * box_size, size * box_size), "white")
    map_draw_context = map_img.load()
    
    colors = {
        1: (255, 100, 100), 2: (100, 100, 255), 3: (255, 255, 100), 4: (200, 200, 200)
    }

    for r, row in enumerate(safe_area_map):
        for c, area_type in enumerate(row):
            is_black = matrix[r][c]
            draw_color = (0, 0, 0) if is_black else (255, 255, 255)
            if area_type in colors:
                draw_color = colors[area_type]

            x_start, y_start = c * box_size, r * box_size
            for i in range(box_size):
                for j in range(box_size):
                    map_draw_context[x_start + i, y_start + j] = draw_color
    
    print("\n次に、機能パターンを正しく色分けした地図を表示します。")
    map_img.show()
    map_img.save("qr_full_safe_area_map.png")

if __name__ == "__main__":
    main()