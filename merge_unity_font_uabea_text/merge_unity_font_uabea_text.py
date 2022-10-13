import argparse
import enum
import pathlib
import re

FILE_ENCODING = "utf-8"
FIELD_NEEDLE_STR_SEP = "->"

class FileType(enum.Enum):
    MONO_BEHAVIOUR = 0
    MATERIAL = 1

class LINE_TYPE(enum.Enum):
    CLASS = enum.auto()
    ARRAY = enum.auto()
    INDEX = enum.auto()
    PAIR_DATA = enum.auto()
    PRIMITIVE = enum.auto()

class Line:    
    def __init__(self, line_str):
        self.line_str = line_str
        self.name = None
        self.type = None
        self.value = None
        self.parent_line = None
        self.field_list = []

OVERWRITE_FIELD_NEEDLE_STR_LIST_DICTS = {
    FileType.MONO_BEHAVIOUR: [
        "Base->m_FaceInfo->m_PointSize",
        "Base->m_FaceInfo->m_Scale",
        "Base->m_FaceInfo->m_LineHeight",
        "Base->m_FaceInfo->m_AscentLine",
        "Base->m_FaceInfo->m_CapLine",
        "Base->m_FaceInfo->m_MeanLine",
        "Base->m_FaceInfo->m_Baseline",
        "Base->m_FaceInfo->m_DescentLine",
        "Base->m_FaceInfo->m_SuperscriptOffset",
        "Base->m_FaceInfo->m_SuperscriptSize",
        "Base->m_FaceInfo->m_SubscriptOffset",
        "Base->m_FaceInfo->m_SubscriptSize",
        "Base->m_FaceInfo->m_UnderlineOffset",
        "Base->m_FaceInfo->m_UnderlineThickness",
        "Base->m_FaceInfo->m_StrikethroughOffset",
        "Base->m_FaceInfo->m_StrikethroughThickness",
        "Base->m_FaceInfo->m_TabWidth",
        "Base->m_GlyphTable",
        "Base->m_CharacterTable",
        "Base->m_UsedGlyphRects",
        "Base->m_FreeGlyphRects",
        "Base->m_AtlasWidth",
        "Base->m_AtlasHeight",
        "Base->m_CreationSettings->pointSize",
        "Base->m_CreationSettings->padding",
        "Base->m_CreationSettings->atlasWidth",
        "Base->m_CreationSettings->atlasHeight",
        "Base->m_CreationSettings->characterSequence",
    ],
    FileType.MATERIAL: {
        "Base->m_SavedProperties->m_Floats": [
            "_TextureHeight",
            "_TextureWidth",
        ],
    },
}
        
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("file_type", help="file_type: 0=MonoBehaviour, 1=Material", type=int)
arg_parser.add_argument("base_file_path_str", help="base_file_path", type=str)
arg_parser.add_argument("merging_file_path_str", help="merging_file_path", type=str)
arg_parser.add_argument("output_file_path_str", help="output_file_path", type=str)
args = arg_parser.parse_args()

def read_file(file_path_str):
    top_line = None
    temp_file_path = pathlib.Path(file_path_str)
    with temp_file_path.open(mode='r', encoding=FILE_ENCODING) as temp_file:
        prev_top_space_count = 0
        temp_parent_line = None
        index_pattern = re.compile(r"\[(\d+)\]")
        for line_str in temp_file.readlines():
            this_line = Line(line_str)

            top_space_count = len(line_str) - len(line_str.lstrip())
            for i in list(range(prev_top_space_count - top_space_count)):
                temp_parent_line = temp_parent_line.parent_line
            
            word_list = line_str.rstrip().split()
            temp_match = index_pattern.search(line_str) 
            if (temp_match is not None):
                this_line.type = LINE_TYPE.INDEX
                this_line.name = temp_match.group(1)
            elif ("=" in word_list):
                this_line.type = LINE_TYPE.PRIMITIVE
                equal_index = word_list.index("=")
                this_line.name = word_list[equal_index - 1]
                this_line.value = word_list[equal_index + 1]
            elif ("Array" in word_list):
                this_line.type = LINE_TYPE.ARRAY
                this_line.name = word_list[word_list.index("Array") + 1]
            elif ("pair" == word_list[1] and "data" == word_list[2]):
                this_line.type = LINE_TYPE.PAIR_DATA
                this_line.name = "pair data"
            else:
                this_line.type = LINE_TYPE.CLASS
                this_line.name = word_list[len(word_list) - 1]
                
            if (top_line is None):
                top_line = this_line
            else:
                this_line.parent_line = temp_parent_line
                temp_parent_line.field_list.append(this_line)
            
            if (this_line.type != LINE_TYPE.PRIMITIVE):    
                temp_parent_line = this_line
            prev_top_space_count = top_space_count
    return top_line

def merge_file(file_type, base_top_line, merging_top_line):
    needle_str_list = OVERWRITE_FIELD_NEEDLE_STR_LIST_DICTS[file_type]
    if (file_type == FileType.MONO_BEHAVIOUR):
        for temp_needle_str in needle_str_list:
            search_and_overwrite_line(base_top_line, merging_top_line, temp_needle_str)
    elif (file_type == FileType.MATERIAL):
        for temp_needle_str in needle_str_list.keys():
            temp_first_value_list = needle_str_list[temp_needle_str]
            if (temp_first_value_list is None):
                search_and_overwrite_line(base_top_line, merging_top_line, temp_needle_str)
            else:
                for temp_first_value in temp_first_value_list:
                    search_and_overwrite_pair_second_line(base_top_line, merging_top_line, temp_first_value)

def search_line(target_line, needle_list):
    needle = needle_list[0]
    if (target_line.name == needle):
        if (len(needle_list) == 1):
            return target_line
        else:
            new_needle_list = needle_list[1:]
            for temp_line in target_line.field_list:
                result_line = search_line(temp_line, new_needle_list)
                if (result_line is not None):
                    return result_line
    return None

def overwrite_line(target_line, new_line):
    parent_line = target_line.parent_line
    parent_field_list = parent_line.field_list
    temp_index = parent_field_list.index(target_line)
    parent_field_list[temp_index] = new_line
    new_line.parent_line = parent_line

def convert_to_field_needle_list(needle_str):
    return needle_str.split(FIELD_NEEDLE_STR_SEP)

def search_and_overwrite_line(base_top_line, merging_top_line, needle_str):
    needle_list = convert_to_field_needle_list(needle_str)
    temp_base_line = search_line(base_top_line, needle_list)
    temp_merging_line = search_line(merging_top_line, needle_list)
    overwrite_line(temp_base_line, temp_merging_line)

def search_pair_second_line(target_line, first_value):
    if (target_line.type == LINE_TYPE.PAIR_DATA):
        field_list = target_line.field_list
        if (field_list[0].value == '"' + first_value + '"'):
            return field_list[1]
        else:
            for temp_line in field_list[1].field_list:
                result_line = search_pair_second_line(temp_line, first_value)
                if (result_line is not None):
                    return result_line
    else:
        for temp_line in target_line.field_list:
            result_line = search_pair_second_line(temp_line, first_value)
            if (result_line is not None):
                return result_line
    return None

def search_and_overwrite_pair_second_line(base_top_line, merging_top_line, first_value):
    temp_base_line = search_pair_second_line(base_top_line, first_value)
    temp_merging_line = search_pair_second_line(merging_top_line, first_value)
    overwrite_line(temp_base_line, temp_merging_line)

def write_file(file_path_str, top_line):
    temp_file_path = pathlib.Path(file_path_str)
    with temp_file_path.open(mode='w', encoding=FILE_ENCODING) as temp_file:
        write_line(temp_file, top_line)

def write_line(target_file, target_line):
    target_file.write(target_line.line_str)
    for temp_line in target_line.field_list:
        write_line(target_file, temp_line)

file_type = FileType(args.file_type)
base_top_line = read_file(args.base_file_path_str)
merging_top_line = read_file(args.merging_file_path_str)
merge_file(file_type, base_top_line, merging_top_line)
write_file(args.output_file_path_str, base_top_line)
