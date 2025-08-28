# scripts/02_module_manipulation.py

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from qrcode.constants import ERROR_CORRECT_H

def print_qr_matrix(matrix):
    """
    QRコードの設計図（行列）をコンソールに分かりやすく表示する関数
    """
    for row in matrix:
        line = ""
        for col in row:
            if col:
                line += "■" # Trueは黒いドット
            else:
                line += "□" # Falseは白いドット
        print(line)

def main():
    data_string = "Hello, Pixel QR Art!"

    # --- ステップ1: QRコードオブジェクトを作成 ---
    # version=2 (25x25) の少し大きめのQRコードで試してみましょう
    qr = qrcode.QRCode(
        version=2,
        error_correction=ERROR_CORRECT_H,
    )
    qr.add_data(data_string)
    qr.make(fit=True)

    # --- ステップ2: QRコードの「設計図(matrix)」を取得 ---
    # qr.modules は True/False が並んだ二次元リストになっています
    matrix = qr.modules
    module_count = qr.modules_count
    
    print(f"QRコードのサイズ: {module_count}x{module_count} ドット")
    print("--- 元の設計図 ---")
    print_qr_matrix(matrix)

    # --- ステップ3: 設計図を書き換える ---
    # 例えば、中央のドットの色を反転させてみます
    # (True -> False, False -> True)
    center_x = module_count // 2
    center_y = module_count // 2
    
    print(f"\n中央のドット ({center_y}, {center_x}) の色を反転させます。")
    # ※ ここでファインダーパターンなど重要な部分を書き換えないように注意が必要です
    # 　 今回は中央なので安全です
    matrix[center_y][center_x] = not matrix[center_y][center_x]

    print("--- 書き換え後の設計図 ---")
    print_qr_matrix(matrix)

    # --- ステップ4: 書き換えた設計図から画像を生成 ---
    # Pillowを使って、設計図から手動で画像を生成します
    box_size = 10 # 1ドットのピクセルサイズ
    border = 4
    image_size = (module_count + border * 2) * box_size
    
    img_custom = Image.new("L", (image_size, image_size), "white")
    
    for r, row in enumerate(matrix):
        for c, col in enumerate(row):
            if col:
                # ドットがTrueなら黒く塗りつぶす
                x = (c + border) * box_size
                y = (r + border) * box_size
                for i in range(box_size):
                    for j in range(box_size):
                        img_custom.putpixel((x + i, y + j), 0) # 0は黒

    print("\n書き換えた設計図から画像を生成しました。")
    img_custom.show()
    
    # --- ステップ5: 読み取りチェック ---
    print("\n--- 読み取りチェック ---")
    decoded_objects = decode(img_custom)
    if decoded_objects:
        decoded_data = decoded_objects[0].data.decode("utf-8")
        print(f"✅ 読み取り成功！ データ: {decoded_data}")
    else:
        print("❌ QRコードを読み取れませんでした。")


if __name__ == "__main__":
    main()

