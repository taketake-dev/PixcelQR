# scripts/03_compare_safe_area.py

import qrcode
from PIL import Image

from qrcode.constants import ERROR_CORRECT_H

def create_original_qr_image(matrix, box_size=20, border=4):
    """
    QRコードの設計図(matrix)から、通常の白黒画像を生成します。
    """
    size = len(matrix)
    # ボーダーを含めた画像サイズを計算
    image_size = (size + border * 2) * box_size
    img = Image.new("L", (image_size, image_size), "white")
    
    # Pillowの描画機能は使わず、ピクセルを直接操作します
    draw_context = img.load()

    for r, row in enumerate(matrix):
        for c, is_black in enumerate(row):
            if is_black:
                # ドットがTrueなら黒く塗りつぶす
                x_start = (c + border) * box_size
                y_start = (r + border) * box_size
                for i in range(box_size):
                    for j in range(box_size):
                        draw_context[x_start + i, y_start + j] = 0 # 0は黒
    return img

def get_safe_area_map(qr_matrix):
    """
    QRコードの設計図から、機能パターン（聖域）を特定し、
    描画可能エリアの地図（マスク）を生成します。
    - 0: データ領域 (描画可能)
    - 1: ファインダーパターン
    - 2: アライメントパターン
    - 3: タイミングパターン
    - 4: フォーマット情報など
    """
    size = len(qr_matrix)
    mask = [[0] * size for _ in range(size)]

    # ファインダーパターン (3つの角) とその周辺
    finder_areas = [(0, 0), (0, size - 8), (size - 8, 0)]
    for y_start, x_start in finder_areas:
        for r in range(8):
            for c in range(8):
                if r == 7 or c == 7:
                    mask[y_start + r][x_start + c] = 4 # 周辺の空白
                else:
                    mask[y_start + r][x_start + c] = 1 # 本体

    # タイミングパターン (6行目と6列目)
    for i in range(8, size - 8):
        mask[6][i] = 3 # 横
        mask[i][6] = 3 # 縦

    # アライメントパターン (バージョン2以上)
    if size >= 25:
        # qrcodeライブラリのバージョンごとのアライメント位置情報を参考にします
        # Version 2 (25x25) の場合、(18, 18) が中心です
        y_center, x_center = 18, 18
        for r in range(-2, 3):
            for c in range(-2, 3):
                mask[y_center + r][x_center + c] = 2

    return mask


def main():
    data_string = "Mapping the sacred areas of QR Code."
    
    qr = qrcode.QRCode(version=2, error_correction=ERROR_CORRECT_H)
    qr.add_data(data_string)
    qr.make(fit=True)
    matrix = qr.modules

    # --- ステップ1: 元のQRコードを生成して表示 ---
    print("まず、元のQRコードを表示します。")
    print("ウィンドウを閉じると、次に進みます。")
    original_img = create_original_qr_image(matrix)
    original_img.show()
    original_img.save("qr_original.png")


    # --- ステップ2: 聖域の地図を取得して色分け表示 ---
    safe_area_map = get_safe_area_map(matrix)

    box_size = 20
    size = len(matrix)
    map_img = Image.new("RGB", (size * box_size, size * box_size), "white")
    map_draw_context = map_img.load()
    
    colors = {
        1: (255, 100, 100), # 赤: ファインダー
        2: (100, 100, 255), # 青: アライメント
        3: (255, 255, 100), # 黄: タイミング
        4: (200, 200, 200), # 灰: その他
    }

    for r, row in enumerate(safe_area_map):
        for c, area_type in enumerate(row):
            original_color_is_black = matrix[r][c]
            
            if area_type == 0: # データ領域
                draw_color = (0, 0, 0) if original_color_is_black else (255, 255, 255)
            else: # 機能パターン領域
                draw_color = colors[area_type]

            x_start, y_start = c * box_size, r * box_size
            for i in range(box_size):
                for j in range(box_size):
                    map_draw_context[x_start + i, y_start + j] = draw_color

    print("\n次に、機能パターンを色分けした地図を表示します。")
    print("赤: ファインダー, 青: アライメント, 黄: タイミング")
    print("白黒のままの部分が、安全に描画できるエリアです。")
    map_img.show()
    map_img.save("qr_safe_area_map.png")

if __name__ == "__main__":
    main()
