setlocal enabledelayedexpansion

set conversionTableDir=.\conversion_table\
set targetDir="./target_text"
set outputDir="./output_text"

for /f "usebackq" %%i in (`dir /b /on %conversionTableDir%*.tsv`) do (
	py replace_simplified_kanji.py "%conversionTableDir%%%i" 0 1 %targetDir% --output %outputDir%
	set skipFlag=1
	goto :firstForEnd
)
:firstForEnd

for /f "usebackq" %%i in (`dir /b /on %conversionTableDir%*.tsv`) do (
	if !skipFlag!==0 (
		py replace_simplified_kanji.py "%conversionTableDir%%%i" 0 1 %outputDir%
	) else (
		set skipFlag=0
	)
)
rem pause
