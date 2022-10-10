import argparse
import pathlib

COMMENT_HEAD = "#"
TSV_SEP = "\t"
FILE_ENCODING = "utf-8"

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("replacer_tsv_path_str", help="replacer_tsv_path", type=str)
arg_parser.add_argument("replacer_tsv_col_index_chn", help="replacer_tsv_col_index_chn", type=int)
arg_parser.add_argument("replacer_tsv_col_index_jap", help="replacer_tsv_col_index_jap", type=int)
arg_parser.add_argument("target_dir_path_str", help="target_dir_path", type=str)
args = arg_parser.parse_args()

def get_replacer_list(target_path_str):
    replacer_list = []
    replacer_tsv_path = pathlib.Path(target_path_str)
    with replacer_tsv_path.open(mode='r', encoding=FILE_ENCODING) as replacer_tsv_file:
        replacer_tsv_list = replacer_tsv_file.readlines()
        do_skip_header = True
        for line_str in replacer_tsv_list:
            if line_str.find(COMMENT_HEAD) == 0:
                continue
            if do_skip_header:
                do_skip_header = False
                continue
            cols = line_str.rstrip().split(TSV_SEP)
            if len(cols) < 2:
                continue
            replacer_tuple = (cols[args.replacer_tsv_col_index_chn], cols[args.replacer_tsv_col_index_jap])
            replacer_list.append(replacer_tuple)
    return replacer_list

def search_dir(replacer_list, target_path):
    if target_path.is_file():
        replace_text(replacer_list, target_path)
    elif target_path.is_dir():
        for temp_path in target_path.iterdir():
            search_dir(replacer_list, temp_path)

def replace_text(replacer_list, target_path):
    file_text = target_path.read_text(FILE_ENCODING)
    for replacer_tuple in replacer_list:
        file_text = file_text.replace(replacer_tuple[0], replacer_tuple[1])
    target_path.write_text(file_text, FILE_ENCODING)

replacer_list = get_replacer_list(args.replacer_tsv_path_str)
target_dir_path = pathlib.Path(args.target_dir_path_str)
search_dir(replacer_list, target_dir_path)
