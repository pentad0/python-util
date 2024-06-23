rem See https://github.com/ClementineAccount/godot-stex-to-png
set targetDir="F:\SteamLibrary\steamapps\common\Cruelty Squad\.import"
set destDir="C:\Temp\Cruelty Squad\stex-png"

for %%i in ("%targetDir:~1,-1%\*.png-*.stex") do (
	py godot-stex-to-png.py "%%i"
)

echo f | xcopy "%targetDir:~1,-1%\*.png" %destDir% /i /y
del "%targetDir:~1,-1%\*.png"
del "%destDir:~1,-1%\*.s3tc.*.png"
