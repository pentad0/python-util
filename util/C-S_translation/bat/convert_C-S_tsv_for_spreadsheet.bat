set tsvDir="../tsv"
set japaneseFile="%tsvDir:~1,-1%/Cruelty-Squad_text_Japanese.tsv"
set englishFile="%tsvDir:~1,-1%/Cruelty-Squad_text_English.tsv"
set outputFile="%tsvDir:~1,-1%/Cruelty-Squad_text_for_spreadsheet.tsv"

py ../py/convert_C-S_tsv_for_spreadsheet.py %japaneseFile% %englishFile% %outputFile%

rem pause
