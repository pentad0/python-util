import argparse
import pathlib

FILE_ENCODING = "utf-8"
GIT_IGNORE = ".gitignore"

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("target_dir_path_str", help="target_dir_path", type=str)
arg_parser.add_argument("export_file_path_str", help="export_file_path", type=str)
args = arg_parser.parse_args()

def get_all_char_list(target_dir_path_str):
    target_dir_path = pathlib.Path(target_dir_path_str)
    temp_list = make_all_char_list(target_dir_path)
    temp_list = list(set(temp_list))
    temp_list.sort()
    return temp_list

def make_all_char_list(target_path):
    temp_list = []
    if target_path.is_file():
        if target_path.name != GIT_IGNORE:
            temp_list = read_file(target_path)
    elif target_path.is_dir():
        for temp_path in target_path.iterdir():
            temp_list.extend(make_all_char_list(temp_path))
    return list(set(temp_list))

def read_file(target_path):
    temp_list = []
    with target_path.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        while temp_line := temp_file.readline():
            temp_list.extend([c for c in temp_line.rstrip()])
    return temp_list

def write_file(export_file_path_str, char_list):
    export_file_path = pathlib.Path(export_file_path_str)
    with export_file_path.open(mode='w', encoding=FILE_ENCODING) as export_file:
        export_file.write("".join(char_list))

char_list = get_all_char_list(args.target_dir_path_str)
write_file(args.export_file_path_str, char_list);
