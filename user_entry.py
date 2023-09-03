from constants import *


class UserEntry:
    def __init__(self):
        self.file_address = FILE_ADDRESS
        self.file_name = FILE_NAME
        self.file_extension = FILE_EXTENSION
        self.folder_path = FOLDER_PATH
        self.file_new_name = ""
        self.file_new_name_append = FILE_NEW_NAME_APPEND
        self.file_new_extension = FILE_NEW_EXTENSION
        self.file_new_folder = FILE_NEW_FOLDER
        self.file_new_address = FILE_NEW_ADDRESS
        self.string1 = ""
        self.string2 = ""
        self.string3 = ""
        self.parse_delim = PARSE_DELIM
        self.parse_ncol = PARSE_NCOL
        self.replace_original = REPLACE_ORIGINAL
        self.replace_new = REPLACE_NEW
        self.n_rows_to_peak_raw = N_ROWS_TO_PEAK_RAW
        self.n_rows_to_peak_modified = N_ROWS_TO_PEAK_MODIFIED
        self.remove_between_1 = REMOVE_BETWEEN_1
        self.remove_between_2 = REMOVE_BETWEEN_2
        self.remove_after = REMOVE_AFTER
        self.marker_option = MARKER_KEEP
        self.replace_option = REPLACE_CUSTOM
        self.parse_delim = PARSE_DELIM
        self.parse_ncol = PARSE_NCOL
        self.split_ncol = SPLIT_NCOL
