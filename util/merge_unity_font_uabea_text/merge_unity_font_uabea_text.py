import argparse
import enum
import sys

sys.path.append('../../lib')
import unity_util

class FileType(enum.Enum):
    FONT_GRYPH = 0
    FONT_MATERIAL = 1

OVERWRITE_FIELD_NEEDLE_STR_LIST_DICTS = {
    FileType.FONT_GRYPH: [
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
    FileType.FONT_MATERIAL: {
        "Base->m_SavedProperties->m_Floats": [
            "_TextureHeight",
            "_TextureWidth",
        ],
    },
}
        
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("file_type", help="file_type: 0=FONT_GRYPH, 1=FONT_MATERIAL", type=int)
arg_parser.add_argument("base_file_path_str", help="base_file_path", type=str)
arg_parser.add_argument("merging_file_path_str", help="merging_file_path", type=str)
arg_parser.add_argument("output_file_path_str", help="output_file_path", type=str)
args = arg_parser.parse_args()

def merge_text(file_type, base_text, merging_text):
    needle_str_list = OVERWRITE_FIELD_NEEDLE_STR_LIST_DICTS[file_type]
    if (file_type == FileType.FONT_GRYPH):
        for temp_needle_str in needle_str_list:
            base_text.search_and_overwrite_line(merging_text, temp_needle_str)
    elif (file_type == FileType.FONT_MATERIAL):
        for temp_needle_str in needle_str_list.keys():
            temp_first_value_list = needle_str_list[temp_needle_str]
            if (temp_first_value_list is None):
                base_text.search_and_overwrite_line(merging_text, temp_needle_str)
            else:
                for temp_first_value in temp_first_value_list:
                    base_text.search_and_overwrite_pair_second_line(merging_text, temp_first_value)

file_type = FileType(args.file_type)
base_text = unity_util.uabe_dumped_text_loader.UabeDumpedText(args.base_file_path_str)
merging_text = unity_util.uabe_dumped_text_loader.UabeDumpedText(args.merging_file_path_str)
merge_text(file_type, base_text, merging_text)
base_text.write_file(args.output_file_path_str)
