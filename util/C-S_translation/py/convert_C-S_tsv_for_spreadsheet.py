from enum import Enum

import argparse
import pathlib

FILE_ENCODING = "utf-8"
TSV_SEP = "\t"
LF = "\n"
MIN_COL_NUM = 4
LINE_TEXT_START_COL_NUM = 5

class TEXT_TYPE(Enum):
    GD = "gd"
    JSON = "json"
    DURATION = "DURATION"
    DYN_LINES = "DYN_LINES"
    LINES = "LINES"
    DIALOG_TEXT = "dialog_text"
    IMPLANT_NAME = "implant_name"
    LEVEL_NAME = "level_name"
    LINE = "line"
    LINE2 = "line2"
    MESSAGE = "message"
    NPC_NAME = "npc_name"
    OVERRIDE_NAME = "override_name"
    TEXT = "text"
    VALUE = "value"
    TSCN_NON_STRING_VALUE = "tscnNonStringValue"
    @classmethod
    def _missing_(cls, value):
        return TEXT_TYPE.TSCN_NON_STRING_VALUE

NON_TARGET_TEXT_TYPES = [
    TEXT_TYPE.DURATION,
    TEXT_TYPE.TSCN_NON_STRING_VALUE,
]

class SpreadsheetCol():
    def __init__(self, index, default_value):
        self.index = index
        self.default_value = default_value

SPREADSHEET_COL_DICT = {}
i = 0
for temp_key, temp_value in {
    "ファイル名" : "",
    "種別" : "",
    "発言者" : "",
    "原文" : "",
    "直訳" : "",
    "ドラフト1" : "",
    "ドラフト2" : "",
    "ドラフト3" : "",
    "備考1" : "",
    "最終稿" : "",
    "備考2" : "",
    "意見" : "",
    "Status" : "",
    "TEXT_TYPE" : "",
    "Key1" : "",
    "Key2" : "",
    "is_text" : "",
}.items():
    SPREADSHEET_COL_DICT[temp_key] = SpreadsheetCol(i, temp_value)
    i += 1

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("input_file_path_japanese_str", help="input_file_path_japanese", type=str)
arg_parser.add_argument("input_file_path_english_str", help="input_file_path_english", type=str)
arg_parser.add_argument("output_file_path_str", help="output_file_path", type=str)
args = arg_parser.parse_args()

def convert_tsv(input_file_path_japanese_str, input_file_path_english_str, output_file_path_str):
    input_file_path_japanese = pathlib.Path(input_file_path_japanese_str)
    input_file_path_english = pathlib.Path(input_file_path_english_str)
    output_file_path = pathlib.Path(output_file_path_str)

    original_text_cols_dict = {}
    with input_file_path_english.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        for line_str in temp_file:
            tsv_col_list = line_str.rstrip(LF).split(TSV_SEP)
            if len(tsv_col_list) >= MIN_COL_NUM:
                tsv_col_list.pop()
                temp_text_type = TEXT_TYPE(tsv_col_list[1])
                if temp_text_type not in (NON_TARGET_TEXT_TYPES + [TEXT_TYPE.GD]):
                    temp_key = get_original_text_key(tsv_col_list)
                    original_text_cols_dict[temp_key] = tsv_col_list

    output_tsv_line_cols_list = []
    with input_file_path_japanese.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        for line_str in temp_file:
            tsv_col_list = line_str.rstrip(LF).split(TSV_SEP)
            if len(tsv_col_list) >= MIN_COL_NUM:
                tsv_col_list.pop()
                temp_text_type = TEXT_TYPE(tsv_col_list[1])
                if temp_text_type not in NON_TARGET_TEXT_TYPES:
                    if temp_text_type != TEXT_TYPE.GD:
                        temp_key = get_original_text_key(tsv_col_list)
                        original_text_cols = original_text_cols_dict[temp_key]
                    match temp_text_type:
                        case TEXT_TYPE.GD:
                            append_output_cols_gd(output_tsv_line_cols_list, tsv_col_list)
                        case TEXT_TYPE.JSON:
                            append_output_cols_json(output_tsv_line_cols_list, tsv_col_list, original_text_cols)
                        case TEXT_TYPE.DYN_LINES | TEXT_TYPE.LINES:
                            append_output_cols_lines(output_tsv_line_cols_list, tsv_col_list, original_text_cols)
                        case _:
                            append_output_cols_tscn_tagged_str(output_tsv_line_cols_list, tsv_col_list, original_text_cols)

    temp_col_names = [""] * len(SPREADSHEET_COL_DICT)
    for temp_key, temp_col in SPREADSHEET_COL_DICT.items():
        temp_col_names[temp_col.index] = temp_key
    output_tsv_line_cols_list.insert(0, temp_col_names)

    output_tsv_line_list = []
    for tsv_col_list in output_tsv_line_cols_list:
        output_tsv_line_list.append(TSV_SEP.join(tsv_col_list))

    with output_file_path.open(mode='w', encoding=FILE_ENCODING) as export_file:
        export_file.write(LF.join(output_tsv_line_list) + LF)

def append_output_cols_gd(line_cols_list, tsv_col_list):
    temp_cols = init_output_cols(tsv_col_list)
    temp_cols[SPREADSHEET_COL_DICT["原文"].index] = tsv_col_list[4]
    temp_cols[SPREADSHEET_COL_DICT["ドラフト1"].index] = tsv_col_list[5]
    line_cols_list.append(temp_cols)

def append_output_cols_json(line_cols_list, tsv_col_list, original_text_cols):
    i = 4
    for temp_kind in [
        "name",
        "objectives",
        "description",
    ]:
        temp_cols = init_output_cols(tsv_col_list)
        temp_cols[SPREADSHEET_COL_DICT["種別"].index] = temp_kind
        temp_cols[SPREADSHEET_COL_DICT["原文"].index] = original_text_cols[i]
        temp_cols[SPREADSHEET_COL_DICT["ドラフト1"].index] = tsv_col_list[i]
        temp_cols[SPREADSHEET_COL_DICT["Key1"].index] = temp_kind
        line_cols_list.append(temp_cols)
        i += 1

def append_output_cols_lines(line_cols_list, tsv_col_list, original_text_cols):
    for i in range(LINE_TEXT_START_COL_NUM, len(tsv_col_list)):
        temp_cols = init_output_cols(tsv_col_list)
        temp_original_text = ""
        if i < len(original_text_cols):
            temp_original_text = original_text_cols[i]
        temp_cols[SPREADSHEET_COL_DICT["原文"].index] = temp_original_text
        temp_cols[SPREADSHEET_COL_DICT["ドラフト1"].index] = tsv_col_list[i]
        temp_cols[SPREADSHEET_COL_DICT["Key1"].index] = tsv_col_list[4]
        temp_cols[SPREADSHEET_COL_DICT["Key2"].index] = str(i - LINE_TEXT_START_COL_NUM)
        line_cols_list.append(temp_cols)

def append_output_cols_tscn_tagged_str(line_cols_list, tsv_col_list, original_text_cols):
    temp_cols = init_output_cols(tsv_col_list)
    temp_cols[SPREADSHEET_COL_DICT["原文"].index] = original_text_cols[5]
    temp_cols[SPREADSHEET_COL_DICT["ドラフト1"].index] = tsv_col_list[5]
    temp_cols[SPREADSHEET_COL_DICT["Key1"].index] = tsv_col_list[4]
    line_cols_list.append(temp_cols)

def get_original_text_key(tsv_col_list):
        temp_key2 = None
        temp_text_type = TEXT_TYPE(tsv_col_list[1])
        if temp_text_type != TEXT_TYPE.GD:
            if temp_text_type != TEXT_TYPE.JSON:
                temp_key2 = tsv_col_list[4]
        return tsv_col_list[0], tsv_col_list[1], temp_key2

def init_output_cols(tsv_col_list):
    temp_cols = [""] * len(SPREADSHEET_COL_DICT)
    for temp_col in SPREADSHEET_COL_DICT.values():
        temp_cols[temp_col.index] = temp_col.default_value
    temp_cols[SPREADSHEET_COL_DICT["ファイル名"].index] = tsv_col_list[0]
    temp_cols[SPREADSHEET_COL_DICT["TEXT_TYPE"].index] = tsv_col_list[1]
    return temp_cols

convert_tsv(args.input_file_path_japanese_str, args.input_file_path_english_str, args.output_file_path_str)
