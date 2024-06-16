from enum import Enum

import argparse
import pathlib

FILE_ENCODING = "utf-8"
TSV_SEP = "\t"
LF = "\n"
LF_STR = "\\n"
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
arg_parser.add_argument("spreadsheet_tsv_file_path_str", help="spreadsheet_tsv_file_path", type=str)
arg_parser.add_argument("input_file_path_str", help="input_file_path", type=str)
arg_parser.add_argument("output_file_path_str", help="output_file_path", type=str)
arg_parser.add_argument("input_column", help="input_column", type=str)
args = arg_parser.parse_args()

def reconvert_tsv(spreadsheet_tsv_file_path_str, input_file_path_str, output_file_path_str, input_column):
    spreadsheet_tsv_file_path = pathlib.Path(spreadsheet_tsv_file_path_str)
    input_file_path = pathlib.Path(input_file_path_str)
    output_file_path = pathlib.Path(output_file_path_str)

    spreadsheet_cols_len = len(SPREADSHEET_COL_DICT)
    line_cols_list = []
    temp_tsv_col_list = []
    is_header_row = True
    with spreadsheet_tsv_file_path.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        for line_str in temp_file:
            if is_header_row:
                is_header_row = False
            else:
                temp_line_cols = line_str.rstrip(LF).split(TSV_SEP)
                
                temp_len = len(temp_tsv_col_list)
                if temp_len > 0:
                    temp_index = temp_len - 1
                    temp_tsv_col_list[temp_index] = temp_tsv_col_list[temp_index] + LF_STR + temp_line_cols.pop(0)
                
                temp_tsv_col_list.extend(temp_line_cols)
                
                if len(temp_tsv_col_list) >= spreadsheet_cols_len:
                    line_cols_list.append(temp_tsv_col_list)
                    temp_tsv_col_list = []

    spreadsheet_tsv_cols_dict = {}
    for tsv_col_list in line_cols_list:
        temp_file_name = tsv_col_list[SPREADSHEET_COL_DICT["ファイル名"].index]
        if temp_file_name not in spreadsheet_tsv_cols_dict:
            spreadsheet_tsv_cols_dict[temp_file_name] = {}
        temp_dict = spreadsheet_tsv_cols_dict[temp_file_name]
        
        temp_text_type = TEXT_TYPE(tsv_col_list[SPREADSHEET_COL_DICT["TEXT_TYPE"].index])
        if temp_text_type not in temp_dict:
            temp_dict[temp_text_type] = {}
        temp_dict = temp_dict[temp_text_type]
        
        temp_original_text = tsv_col_list[SPREADSHEET_COL_DICT["原文"].index]
        temp_final_draft = tsv_col_list[SPREADSHEET_COL_DICT[input_column].index]
        temp_key1 = tsv_col_list[SPREADSHEET_COL_DICT["Key1"].index]
        temp_key2 = tsv_col_list[SPREADSHEET_COL_DICT["Key2"].index]
        if temp_text_type not in NON_TARGET_TEXT_TYPES:
            match temp_text_type:
                case TEXT_TYPE.GD:
                    temp_dict[temp_original_text] = temp_final_draft
                case TEXT_TYPE.DYN_LINES | TEXT_TYPE.LINES:
                    if temp_key1 not in temp_dict:
                        temp_dict[temp_key1] = {}
                    temp_dict[temp_key1][temp_key2] = temp_final_draft
                case _:
                    temp_dict[temp_key1] = temp_final_draft

    output_tsv_line_cols_list = []
    with input_file_path.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        for line_str in temp_file:
            tsv_col_list = line_str.rstrip(LF).split(TSV_SEP)
            output_tsv_line_cols_list.append(tsv_col_list)
            if len(tsv_col_list) >= MIN_COL_NUM + 1:
                temp_text_type = TEXT_TYPE(tsv_col_list[1])
                if temp_text_type not in NON_TARGET_TEXT_TYPES:
                    temp_file_name = tsv_col_list[0]
                    if temp_file_name in spreadsheet_tsv_cols_dict and temp_text_type in spreadsheet_tsv_cols_dict[temp_file_name]:
                        temp_dict = spreadsheet_tsv_cols_dict[temp_file_name][temp_text_type]
                        temp_tag_str = tsv_col_list[4]
                        match temp_text_type:
                            case TEXT_TYPE.JSON:
                                for temp_kind, temp_index in {
                                    "name" : 4,
                                    "objectives" : 5,
                                    "description" : 6,
                                }.items():
                                    if temp_kind in temp_dict:
                                        tsv_col_list[temp_index] = temp_dict[temp_kind]
                            case TEXT_TYPE.DYN_LINES | TEXT_TYPE.LINES:
                                if temp_tag_str in temp_dict:
                                    for temp_key2, temp_str in temp_dict[temp_tag_str].items():
                                        tsv_col_list[LINE_TEXT_START_COL_NUM + int(temp_key2)] = temp_str
                            case _:
                                if temp_tag_str in temp_dict:
                                    tsv_col_list[5] = temp_dict[temp_tag_str]

    output_tsv_line_list = []
    for tsv_col_list in output_tsv_line_cols_list:
        output_tsv_line_list.append(TSV_SEP.join(tsv_col_list))

    with output_file_path.open(mode='w', encoding=FILE_ENCODING) as export_file:
        export_file.write(LF.join(output_tsv_line_list) + LF)

reconvert_tsv(args.spreadsheet_tsv_file_path_str, args.input_file_path_str, args.output_file_path_str, args.input_column)
