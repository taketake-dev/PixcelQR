# scripts/04_dynamic_safe_area.py

import qrcode
from PIL import Image

# QRコードのバージョン毎のアライメントパターンの中心座標のリスト
# 仕様書から引用したデータです
ALIGNMENT_PATTERN_COORDS = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    # ... より大きなバージョンも続く
}

def get_qr_version(matrix):
    """
    QRコードのサイズ(モジュール数)からバージョンを計算する
    """
    size = len(matrix)
    return (size - 21) // 4 + 1

def get_safe_area_map(matrix):
    """
    QRコードの設計図から、機能パターン（聖域）を動的に特定し、
    描画可能エリアの地図（マスク）を生成します。
    """
    size = len(matrix)
    version = get_qr_version(matrix)
    mask = [[0] * size for _ in range(size)]

    # --- ファインダーパターンとセパレータ ---
    for y_start in (0, size - 8):
        for x_start in (0, size - 8):
            # 3つの角のうち、右下は対象外
            if y_start > 0 and x_start > 0:
                continue
            for r in range(8):
                for c in range(8):
                    if r == 7 or c == 7:
                        mask[y_start + r][x_start + c] = 4 # セパレータ(灰)
                    else:
                        mask[y_start + r][x_start + c] = 1 # ファインダー(赤)
    
    # --- タイミングパターン ---
    for i in range(8, size - 8):
        mask[6][i] = 3 # 横
        mask[i][6] = 3 # 縦

    # --- アライメントパターン (バージョンに応じた位置) ---
    if version in ALIGNMENT_PATTERN_COORDS:
        coords = ALIGNMENT_PATTERN_COORDS[version]
        # 座標のすべての組み合わせをループ
        for y_center in coords:
            for x_center in coords:
                # ファインダーパターンの近くは描画しない
                is_near_finder = (y_center < 9 and x_center < 9) or \
                                 (y_center < 9 and x_center > size - 9) or \
                                 (y_center > size - 9 and x_center < 9)
                if is_near_finder:
                    continue
                
                # 5x5のパターンを描画
                for r in range(-2, 3):
                    for c in range(-2, 3):
                        mask[y_center + r][x_center + c] = 2 # アライメント(青)

    return mask

def main():
    data_string = "A more robust way to map the sacred areas of any QR Code version."
    
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data_string)
    qr.make(fit=True)
    matrix = qr.modules
    version = get_qr_version(matrix)
    size = len(matrix)
    print(f"データ量に合わせて、バージョン{version} ({size}x{size}マス)のQRコードが生成されました。")

    # --- 元のQRコードを表示 ---
    original_img = qrcode.make(data_string, error_correction=qrcode.constants.ERROR_CORRECT_H)
    print("まず、元のQRコードを表示します。")
    original_img.show()

    # --- 聖域の地図を生成して表示 ---
    safe_area_map = get_safe_area_map(matrix)
    
    box_size = 15 # 少し小さくして見やすくします
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
            is_black = matrix[r][c]
            draw_color = (0, 0, 0) if is_black else (255, 255, 255) # デフォルトは元の色
            if area_type in colors:
                draw_color = colors[area_type]

            x_start, y_start = c * box_size, r * box_size
            for i in range(box_size):
                for j in range(box_size):
                    map_draw_context[x_start + i, y_start + j] = draw_color
    
    print("\n次に、機能パターンを正しく色分けした地図を表示します。")
    map_img.show()
    map_img.save("qr_dynamic_safe_area_map.png")

if __name__ == "__main__":
    main()
