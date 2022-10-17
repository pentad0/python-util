set targetDir=./target_text

py merge_unity_font_uabea_text.py 0 "%targetDir%/base.txt" "%targetDir%/merge.txt" "%targetDir%/output.txt"
py merge_unity_font_uabea_text.py 1 "%targetDir%/baseMaterial.txt" "%targetDir%/mergeMaterial.txt" "%targetDir%/outputMaterial.txt"
rem pause
