set conversionTableDir=.\conversion_table\
set targetDir="./target_text"

for /f "usebackq" %%i in (`dir /b /on %conversionTableDir%*.tsv`) do (
	py replace_simplified_kanji.py "%conversionTableDir%%%i" 0 1 %targetDir%
)
rem pause
