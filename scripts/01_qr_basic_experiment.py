# scripts/01_qr_experiment.py

import qrcode
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode

from qrcode.constants import ERROR_CORRECT_H

def main():
    # --- 実験1：QRコードを生成して表示する ---
    print("--- 実験1：QRコード生成 ---")
    data_string = "https://www.ah-soft.com/vocaloid/yukari/"

    qr: qrcode.QRCode = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data_string)
    qr.make(fit=True)
    img= qr.make_image(fill_color="black", back_color="white")

    # .pyスクリプトでは .show() を使うと画像ビューアで表示される
    print("生成したQRコードを表示します... (ウィンドウを閉じると次に進みます)")
    img.show()
    img.save("basic_qr.png")
    print("basic_qr.pngとして保存しました。")
    
    # --- 実験2：QRコードを「画像」として加工する ---
    print("\n--- 実験2：画像加工 ---")
    img_editable = img.copy()
    draw = ImageDraw.Draw(img_editable)

    image_width, image_height = img_editable.size
    rect_start_x = image_width * 0.4
    rect_start_y = image_height * 0.4
    rect_end_x = image_width * 0.6
    rect_end_y = image_height * 0.6

    draw.rectangle(
        (rect_start_x, rect_start_y, rect_end_x, rect_end_y), 
        fill="purple"
    )
    
    print("加工したQRコードを表示します... (ウィンドウを閉じると次に進みます)")
    img_editable.show()
    edited_filename = "edited_qr.png"
    img_editable.save(edited_filename)
    print(f"{edited_filename}として保存しました。")

    # --- 実験3：加工したQRコードがまだ読めるかチェックする ---
    print("\n--- 実験3：読み取りチェック ---")
    try:
        decoded_objects = decode(Image.open(edited_filename))
        if decoded_objects:
            decoded_data = decoded_objects[0].data.decode("utf-8")
            print(f"✅ 読み取り成功！ データ: {decoded_data}")
            if decoded_data == data_string:
                print("元のデータと一致しました。")
        else:
            print("❌ QRコードを読み取れませんでした。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# このファイルが直接実行されたらmain()を呼び出す
if __name__ == "__main__":
    main()