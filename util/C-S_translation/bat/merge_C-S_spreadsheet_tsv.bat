set tsvDir="../tsv"
set spreadsheetTsvFile="%tsvDir:~1,-1%/Cruelty-Squad_text_for_spreadsheet_mod.tsv"
set inputFile="%tsvDir:~1,-1%/Cruelty-Squad_text_Japanese.tsv"
set outputFile="%tsvDir:~1,-1%/Cruelty-Squad_text_Japanese_merged.tsv"

py ../py/merge_C-S_spreadsheet_tsv.py %spreadsheetTsvFile% %inputFile% %outputFile%

rem pause
