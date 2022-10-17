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

    LINE_STR_SEP = " "
    """Separator of line string.
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
        PAIR = enum.auto()
        PRIMITIVE = enum.auto()

    class Line:    
        """Object of line.
    
        Attributes:
            line_str (string): string of whole line
            line_type (:obj:`UabeDumpedText.LINE_TYPE`): type of line
            type (string): type of field
            name (string): name of field
            value (string): value of field
            parent (string): parent of line
            children (list): child line list
        """

        def __init__(self, line_str):
            self.line_str = line_str
            self.line_type = None
            self.type = None
            self.name = None
            self.value = None
            self.parent = None
            self.children = []

            self.setAttributes()

        def __str__(self):
            return self.line_strmpName
        
        def setAttributes(self):
            word_list = self.line_str.strip().split(UabeDumpedText.LINE_STR_SEP)
            temp_match = re.search(r"\[(\d+)\]", self.line_str) 
            if (temp_match is not None):
                self.line_type = UabeDumpedText.LINE_TYPE.INDEX
                self.name = temp_match.group(1)
            elif ("=" in word_list):
                self.line_type = UabeDumpedText.LINE_TYPE.PRIMITIVE
                temp_index = word_list.index("=")
                self.type = word_list[temp_index - 2]
                self.name = word_list[temp_index - 1]
                if (self.type == "string"):
                    temp_value = UabeDumpedText.LINE_STR_SEP.join(word_list[temp_index + 1:])
                    self.value = temp_value[1:len(temp_value) - 1]
                else:
                    self.value = word_list[temp_index + 1]
            elif ("Array" in word_list):
                self.line_type = UabeDumpedText.LINE_TYPE.ARRAY
                temp_index = word_list.index("Array")
                self.type = word_list[temp_index]
                self.name = word_list[temp_index + 1]
            elif ("pair" == word_list[1] and "data" == word_list[2]):
                self.line_type = UabeDumpedText.LINE_TYPE.PAIR
                self.type = word_list[1]
                self.name = word_list[2]
            else:
                self.line_type = UabeDumpedText.LINE_TYPE.CLASS
                temp_index = len(word_list) - 1
                self.type = word_list[temp_index - 1]
                self.name = word_list[temp_index]
        
        def setValue(self, value):
            if (self.value is None):
                raise Exception("No value line type.")
            else:
                self.value = value

                temp_line_str = self.line_str.rstrip()
                last_spaces = self.line_str[len(temp_line_str):]
                temp_line_str = temp_line_str[0:temp_line_str.index(" = ") + 3]
                if (self.type == "string"):
                    temp_line_str += '"' + value + '"'
                else:
                    temp_line_str += value

                self.line_str = temp_line_str + last_spaces
    
    def __init__(self, text_file_path_str):
        temp_file_path = pathlib.Path(text_file_path_str)
        self.root_line = UabeDumpedText.__read_text_file(temp_file_path)
        self.name = temp_file_path.name

    @staticmethod
    def __read_text_file(file_path):
        root_line = None
        with file_path.open(mode='r', encoding=UabeDumpedText.TEXT_FILE_ENCODING) as temp_file:
            prev_top_space_count = 0
            temp_parent = None
            for line_str in temp_file.readlines():
                this_line = UabeDumpedText.Line(line_str)
                
                top_space_count = len(line_str) - len(line_str.lstrip())

                if (root_line is None):
                    root_line = this_line
                else:
                    for i in list(range(prev_top_space_count - top_space_count)):
                        temp_parent = temp_parent.parent
                    
                    this_line.parent = temp_parent
                    temp_parent.children.append(this_line)
                
                if (this_line.line_type != UabeDumpedText.LINE_TYPE.PRIMITIVE):
                    temp_parent = this_line
                
                prev_top_space_count = top_space_count
        return root_line

    def __search_line(self, target_line, needle_list):
        if (target_line.name == needle_list[0]):
            if (len(needle_list) == 1):
                return target_line
            else:
                new_needle_list = needle_list[1:]
                for temp_line in target_line.children:
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
        parent = target_line.parent
        parent_children = parent.children
        temp_index = parent_children.index(target_line)
        parent_children[temp_index] = new_line
        new_line.parent = parent

    def search_and_overwrite_line(self, new_dumped_text, needle_str):
        temp_base_line = self.search_line(needle_str)
        temp_new_line = new_dumped_text.search_line(needle_str)
        UabeDumpedText.overwrite_line(temp_base_line, temp_new_line)

    def __search_pair_second_line(self, target_line, first_value):
        if (target_line.line_type == UabeDumpedText.LINE_TYPE.PAIR):
            children = target_line.children
            if (children[0].value == first_value):
                return children[1]
            else:
                for temp_line in children[1].children:
                    result_line = self.__search_pair_second_line(temp_line, first_value)
                    if (result_line is not None):
                        return result_line
        else:
            for temp_line in target_line.children:
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
        for temp_line in target_line.children:
            UabeDumpedText.__write_line(target_file, temp_line)

    def write_file(self, file_path_str):
        temp_file_path = pathlib.Path(file_path_str)
        with temp_file_path.open(mode='w', encoding=UabeDumpedText.TEXT_FILE_ENCODING) as temp_file:
            UabeDumpedText.__write_line(temp_file, self.root_line)
