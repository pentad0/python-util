set tsvDir="../tsv"
set spreadsheetTsvFile="%tsvDir:~1,-1%/Cruelty-Squad_text_for_spreadsheet_mod.tsv"
set inputFile="%tsvDir:~1,-1%/Cruelty-Squad_text_Japanese.tsv"
set outputFile="%tsvDir:~1,-1%/Cruelty-Squad_text_Japanese_reconvert.tsv"

py ../py/reconvert_C-S_tsv_for_spreadsheet.py %spreadsheetTsvFile% %inputFile% %outputFile%

rem pause
