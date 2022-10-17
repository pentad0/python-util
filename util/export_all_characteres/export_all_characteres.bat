rem set targetDir="./target_text"
rem set targetDir="../replace_simplified_kanji/target_text"
set targetDir="../replace_simplified_kanji/output_text"

py export_all_characteres.py %targetDir% ./export/all_characteres.txt
rem py export_all_characteres.py %targetDir% ./export/all_characteres.txt --sep_lf
rem pause
