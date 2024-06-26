# C-S_translation
/tsvフォルダに対象tsvファイルを配置して/bat/*.batを実行すると、同じフォルダに処理後のファイルが作成される。

## /bat/godot-stex-to-png-all.bat
ゲームの.importに含まれる.pngファイルを抽出する。  
抽出処理自体は下記のスクリプトに任せている。  
https://github.com/ClementineAccount/godot-stex-to-png

## /py/convert_C-S_tsv_for_spreadsheet.py
日本語と英語のtsvファイルからスプレッドシート貼り付け用tsvファイルを作成する。

## /py/merge_C-S_spreadsheet_tsv.py
スプレッドシート貼り付け用tsvファイルを日本語tsvファイルにマージする。
