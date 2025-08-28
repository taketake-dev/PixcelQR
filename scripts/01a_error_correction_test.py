# scripts/01a_error_correction_test.py

import qrcode
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode
import os

from qrcode.constants import ERROR_CORRECT_H

def check_readability(image, original_data):
    """
    画像からQRコードを読み取り、データが一致するかをチェックする関数
    """
    try:
        decoded_objects = decode(image)
        if decoded_objects:
            decoded_data = decoded_objects[0].data.decode("utf-8")
            if decoded_data == original_data:
                return True, f"✅ 読み取り成功！ データ: {decoded_data}"
            else:
                return False, f"⚠️ 読み取り成功しましたが、データが一致しませんでした。"
        else:
            return False, "❌ QRコードを読み取れませんでした。"
    except Exception as e:
        return False, f"エラーが発生しました: {e}"

def main():
    data_string = "https://www.ah-soft.com/taketake/"
    
    # 実験結果を保存するフォルダを作成
    output_dir = "error_test_results"
    os.makedirs(output_dir, exist_ok=True)
    print(f"'{output_dir}/' フォルダに実験結果を保存します。")

    # QRコードの元画像を生成
    qr: qrcode.QRCode = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data_string)
    qr.make(fit=True)
    base_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # 塗りつぶす割合を10%から2%刻みで試す
    for percentage in range(30, 101, 1):
        print(f"\n--- 中央を {percentage}% 塗りつぶす実験 ---")
        
        # 元の画像をコピーして加工する
        img_editable = base_img.copy()
        draw = ImageDraw.Draw(img_editable)

        # 塗りつぶす領域を計算
        image_width, image_height = img_editable.size
        # QRコード部分のみのサイズを考慮 (ボーダーを引く)
        border_pixels = 4 * 10 # border * box_size
        qr_area_size = image_width - 2 * border_pixels
        
        rect_size = qr_area_size * (percentage / 100.0)
        offset = (qr_area_size - rect_size) / 2
        
        x0 = border_pixels + offset
        y0 = border_pixels + offset
        x1 = x0 + rect_size
        y1 = y0 + rect_size

        # 四角形を描画
        draw.rectangle((x0, y0, x1, y1), fill="purple")

        # ファイルに保存
        filename = os.path.join(output_dir, f"qr_filled_{percentage}percent.png")
        img_editable.save(filename)
        print(f"'{filename}' を保存しました。")

        # 読み取りチェック
        is_readable, message = check_readability(img_editable, data_string)
        print(message)

        # 読み取れなくなったら実験を終了
        if not is_readable:
            print("\nこれ以上塗りつぶすと読み取れないようです。実験を終了します。")
            break

if __name__ == "__main__":
    main()

