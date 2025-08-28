# scripts/01_generate_and_color_qr.py

# 必要なライブラリをインポートします
import qrcode
from PIL import Image

def create_qr_with_color(data, output_filename, box_size=10, border=4, fill_color="red", back_color="white"):
    """
    指定した色でQRコードを生成する簡単なテスト関数です。
    """
    try:
        # QRコードオブジェクトを作成します
        # 誤り訂正レベルを最も高い「H」に設定してみましょう
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # type: ignore
            box_size=box_size,
            border=border,
        )

        # QRコードにしたいデータを追加します
        qr.add_data(data)
        qr.make(fit=True)

        # QRコードの画像オブジェクトを生成します
        # fill_colorでドットの色、back_colorで背景色を指定できます
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # 画像をファイルとして保存します
        img.save(output_filename)
        print(f"'{output_filename}' を作成しました。")

        # 保存した画像をスマートフォンで読み取れるか試してみましょう
        # 赤色でも、コントラストがはっきりしていれば読み取れることが多いですよ

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# このスクリプトが直接実行されたときに以下のコードが動きます
if __name__ == "__main__":
    # QRコードにしたい情報
    my_data = "Hello, Yuzuki Yukari!"
    
    # 保存するファイル名
    filename = "test_qr_red.png"
    
    # 関数を呼び出してQRコードを生成します
    create_qr_with_color(my_data, filename, fill_color="purple")

