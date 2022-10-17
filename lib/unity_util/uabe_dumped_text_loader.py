"""uabe_dumped_text_loader

Load text dumped by UABE (Unity Assets Bundle Extractor) as an object.

"""
import enum
import pathlib
import re

class UabeDumpedText:
    """Object from dumped text by UABE (Unity Assets Bundle Extractor).

    Attributes:
        root_line (:obj:`UabeDumpedText.Line`): line of root
        name (string): name
    """
    
    TEXT_FILE_ENCODING = "utf-8"
    """Encoding of dumped text.
    """

    FIELD_HIERARCHY_STR_SEP = "->"
    """Separator of object field hierarchy string.

    Examples:
        Base->m_FaceInfo->m_PointSize
    """

    class LINE_TYPE(enum.Enum):
        """Type of line.
        """
        CLASS = enum.auto()
        ARRAY = enum.auto()
        INDEX = enum.auto()
        PAIR_DATA = enum.auto()
        PRIMITIVE = enum.auto()

    class Line:    
        """Object of line.
    
        Attributes:
            line_str (string): string of whole line
            name (string): name of field
            type (string): type of field
            value (string): value of field
            parent_line (string): parent of line
            child_field_list (list): child field list
        """

        def __init__(self, line_str):
            self.line_str = line_str
            self.name = None
            self.type = None
            self.value = None
            self.parent_line = None
            self.child_field_list = []

        def __str__(self):
            tempName = self.line_str
            return tempName
    
    def __init__(self, text_file_path_str):
        temp_file_path = pathlib.Path(text_file_path_str)
        self.root_line = UabeDumpedText.__read_text_file(temp_file_path)
        self.name = temp_file_path.name
    
    @staticmethod
    def __read_text_file(file_path):
        root_line = None
        with file_path.open(mode='r', encoding=UabeDumpedText.TEXT_FILE_ENCODING) as temp_file:

            prev_top_space_count = 0
            temp_parent_line = None
            index_pattern = re.compile(r"\[(\d+)\]")
            for line_str in temp_file.readlines():
                this_line = UabeDumpedText.Line(line_str)

                top_space_count = len(line_str) - len(line_str.lstrip())
                for i in list(range(prev_top_space_count - top_space_count)):
                    temp_parent_line = temp_parent_line.parent_line
                
                word_list = line_str.rstrip().split()
                temp_match = index_pattern.search(line_str) 
                if (temp_match is not None):
                    this_line.type = UabeDumpedText.LINE_TYPE.INDEX
                    this_line.name = temp_match.group(1)
                elif ("=" in word_list):
                    this_line.type = UabeDumpedText.LINE_TYPE.PRIMITIVE
                    equal_index = word_list.index("=")
                    this_line.name = word_list[equal_index - 1]
                    this_line.value = word_list[equal_index + 1]
                elif ("Array" in word_list):
                    this_line.type = UabeDumpedText.LINE_TYPE.ARRAY
                    this_line.name = word_list[word_list.index("Array") + 1]
                elif ("pair" == word_list[1] and "data" == word_list[2]):
                    this_line.type = UabeDumpedText.LINE_TYPE.PAIR_DATA
                    this_line.name = "pair data"
                else:
                    this_line.type = UabeDumpedText.LINE_TYPE.CLASS
                    this_line.name = word_list[len(word_list) - 1]
                    
                if (root_line is None):
                    root_line = this_line
                else:
                    this_line.parent_line = temp_parent_line
                    temp_parent_line.child_field_list.append(this_line)
                
                if (this_line.type != UabeDumpedText.LINE_TYPE.PRIMITIVE):
                    temp_parent_line = this_line
                prev_top_space_count = top_space_count
        return root_line

    def __search_line(self, target_line, needle_list):
        if (target_line.name == needle_list[0]):
            if (len(needle_list) == 1):
                return target_line
            else:
                new_needle_list = needle_list[1:]
                for temp_line in target_line.child_field_list:
                    result_line = self.__search_line(temp_line, new_needle_list)
                    if (result_line is not None):
                        return result_line
        return None

    @staticmethod
    def convert_to_field_hierarchy_list(field_hierarchy_str):
        return field_hierarchy_str.split(UabeDumpedText.FIELD_HIERARCHY_STR_SEP)

    def search_line(self, needle_str):
        needle_list = UabeDumpedText.convert_to_field_hierarchy_list(needle_str)
        return self.__search_line(self.root_line, needle_list)

    @staticmethod
    def overwrite_line(target_line, new_line):
        parent_line = target_line.parent_line
        parent_child_field_list = parent_line.child_field_list
        temp_index = parent_child_field_list.index(target_line)
        parent_child_field_list[temp_index] = new_line
        new_line.parent_line = parent_line

    def search_and_overwrite_line(self, new_dumped_text, needle_str):
        temp_base_line = self.search_line(needle_str)
        temp_new_line = new_dumped_text.search_line(needle_str)
        UabeDumpedText.overwrite_line(temp_base_line, temp_new_line)

    def __search_pair_second_line(self, target_line, first_value):
        if (target_line.type == UabeDumpedText.LINE_TYPE.PAIR_DATA):
            child_field_list = target_line.child_field_list
            if (child_field_list[0].value == '"' + first_value + '"'):
                return child_field_list[1]
            else:
                for temp_line in child_field_list[1].child_field_list:
                    result_line = self.__search_pair_second_line(temp_line, first_value)
                    if (result_line is not None):
                        return result_line
        else:
            for temp_line in target_line.child_field_list:
                result_line = self.__search_pair_second_line(temp_line, first_value)
                if (result_line is not None):
                    return result_line
        return None

    def search_pair_second_line(self, first_value):
        return self.__search_pair_second_line(self.root_line, first_value)

    def search_and_overwrite_pair_second_line(self, new_dumped_text, first_value):
        temp_base_line = self.search_pair_second_line(first_value)
        temp_new_line = new_dumped_text.search_pair_second_line(first_value)
        UabeDumpedText.overwrite_line(temp_base_line, temp_new_line)

    @staticmethod
    def __write_line(target_file, target_line):
        target_file.write(target_line.line_str)
        for temp_line in target_line.child_field_list:
            UabeDumpedText.__write_line(target_file, temp_line)

    def write_file(self, file_path_str):
        temp_file_path = pathlib.Path(file_path_str)
        with temp_file_path.open(mode='w', encoding=UabeDumpedText.TEXT_FILE_ENCODING) as temp_file:
            UabeDumpedText.__write_line(temp_file, self.root_line)
