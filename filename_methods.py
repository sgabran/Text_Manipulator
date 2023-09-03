# ver = 2022-1-8-1

import os
import os.path


class FileNameMethods:

    @staticmethod
    def build_file_name_full(file_location, file_name, file_suffix):
        try:
            file_name_full = os.path.join(file_location, file_name + file_suffix)
            return file_name_full
        except Exception:
            return None

    @staticmethod
    def check_filename_components_exists(file_location, file_name, file_suffix):
        result = os.path.isfile(FileNameMethods.build_file_name_full(file_location, file_name, file_suffix))
        return result

    @staticmethod
    def check_filename_full_exists(filename_full):
        result = os.path.isfile(filename_full)
        return result

    @staticmethod
    def check_file_location_valid(file_location):
        folder_valid = os.path.isdir(file_location)
        return folder_valid

    @staticmethod
    def split_file_full_name(file_full_name):
        try:
            folder, filename_with_extension = os.path.split(file_full_name)
            filename, extension = os.path.splitext(filename_with_extension)
            return folder, filename, extension
        except Exception as e:
            print(f'An error occurred: {str(e)}')
