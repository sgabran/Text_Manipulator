# 2023-9-4

import os
import os.path
from idlelib.tooltip import *
from tkinter import filedialog
from tkinter import messagebox
import csv

import sys
import shutil

import filename_methods as fm
import misc_methods as mm
from constants import *
from session_log import SessionLog
from user_entry import UserEntry


# Class to create GUI
class MainWindow:
    # Dependencies: MainWindow communicate with classes that are related to GUI contents and buttons
    def __init__(self):  # instantiation function. Use root for GUI and refers to main window

        root = Tk()
        root.title("Text Manipulator")
        self.root_frame = root
        self.user_entry = UserEntry()
        self.session_log = SessionLog(self.user_entry)

        self.files_to_process = []
        self.files_moved_fullpath = []
        self.folders_created_fullpath = []
        self.bad_undo_folder = {}
        self.n_files_to_process = 0
        self.n_files_moved_fullpath = 0
        self.n_folders_created_fullpath = 0
        self.n_restored_files = 0
        self.n_deleted_folders = 0
        self.finished_with_errors = 1

        self.file_contents_raw = ""
        self.file_contents_raw_list = []
        self.file_contents_modified = ""
        self.file_contents_modified_list = []

        # GUI Frames
        # self.frame_root_title = Frame(root, highlightthickness=10)
        # self.frame_file = LabelFrame(root, width=120, height=100, padx=5, pady=5, text="Session")
        # self.frame_operations = LabelFrame(root, width=120, height=600, padx=5, pady=5, text="Operations")
        self.frame_root_session = Frame(root)
        self.frame_file = LabelFrame(self.frame_root_session, text="File")
        self.frame_operations = LabelFrame(self.frame_root_session, text="Operations")
        self.frame_root_output = Frame(root)
        self.frame_review = LabelFrame(self.frame_root_output, width=300, height=200, padx=5, pady=5, text="Review")

        # Disable resizing the window
        root.resizable(False, False)

        entry_validation_positive_numbers = root.register(mm.only_positive_numbers)
        entry_validation_positive_numbers_nonzero = root.register(mm.only_positive_numbers_nonzero)
        entry_validation_numbers = root.register(mm.only_digits)
        entry_validation_numbers_space = root.register(mm.digits_or_space)
        entry_validation_positive_numbers_comma = root.register(mm.positive_numbers_or_comma)

        # Grids
        self.frame_root_session.grid    (row=0, column=0)
        self.frame_root_output.grid     (row=0, column=1)
        self.frame_file.grid       (row=0, column=0, sticky="NE", padx=10, pady=(5, 5), ipadx=5, ipady=2)
        self.frame_operations.grid (row=1, column=0, sticky="NE", padx=10, pady=(5, 5), ipadx=5, ipady=0)
        self.frame_review.grid     (row=0, column=1, padx=10, pady=(5, 5), ipadx=5, ipady=2)

        ######################################################################
        # Frame Session

        # Labels
        label_replace = Label(self.frame_operations, text="With")
        label_remove_between = Label(self.frame_operations, text="And")
        label_parse_delim = Label(self.frame_operations, text="Delimiter")
        label_parse_ncol = Label(self.frame_operations, text="Columns")

        # Entries
        self.entry_file_address_entry = StringVar()
        self.entry_file_address_entry.trace("w", lambda name, index, mode, entry_file_address_entry=self.entry_file_address_entry: self.entry_update_file_address())
        self.entry_file_address = Entry(self.frame_file, width=80, textvariable=self.entry_file_address_entry)
        self.entry_file_address.insert(END, os.path.normcase(FOLDER_PATH))

        self.entry_replace_original_entry = StringVar()
        self.entry_replace_original_entry.trace("w", lambda name, index, mode, entry_replace_original_entry=self.entry_replace_original_entry: self.entry_update_replace_original())
        self.entry_replace_original = Entry(self.frame_operations, width=20, textvariable=self.entry_replace_original_entry)

        self.entry_replace_new_entry = StringVar()
        self.entry_replace_new_entry.trace("w", lambda name, index, mode, entry_replace_new_entry=self.entry_replace_new_entry: self.entry_update_replace_new())
        self.entry_replace_new = Entry(self.frame_operations, width=20, textvariable=self.entry_replace_new_entry)

        self.entry_remove_between_1_entry = StringVar()
        self.entry_remove_between_1_entry.trace("w", lambda name, index, mode, entry_remove_between_1_entry=self.entry_remove_between_1_entry: self.entry_update_remove_between_1())
        self.entry_remove_between_1 = Entry(self.frame_operations, width=20, textvariable=self.entry_remove_between_1_entry)

        self.entry_remove_between_2_entry = StringVar()
        self.entry_remove_between_2_entry.trace("w", lambda name, index, mode, entry_remove_between_2_entry=self.entry_remove_between_2_entry: self.entry_update_remove_between_2())
        self.entry_remove_between_2 = Entry(self.frame_operations, width=20, textvariable=self.entry_remove_between_2_entry)

        self.entry_remove_after_entry = StringVar()
        self.entry_remove_after_entry.trace("w", lambda name, index, mode, entry_remove_after_entry=self.entry_remove_after_entry: self.entry_update_remove_after())
        self.entry_remove_after = Entry(self.frame_operations, width=10, textvariable=self.entry_remove_after_entry)

        self.entry_parse_delim_entry = StringVar()
        self.entry_parse_delim_entry.trace("w", lambda name, index, mode, entry_parse_delim_entry=self.entry_parse_delim_entry: self.entry_update_parse_delim())
        self.entry_parse_delim = Entry(self.frame_operations, width=7, textvariable=self.entry_parse_delim_entry)

        self.entry_parse_ncol_entry = StringVar()
        self.entry_parse_ncol_entry.trace("w", lambda name, index, mode, entry_parse_ncol_entry=self.entry_parse_ncol_entry: self.entry_update_parse_ncol())
        self.entry_parse_ncol = Entry(self.frame_operations, width=7, textvariable=self.entry_parse_ncol_entry, validate="key", validatecommand=(entry_validation_positive_numbers_nonzero, '%P'))

        self.entry_split_to_columns_entry = StringVar()
        self.entry_split_to_columns_entry.trace("w", lambda name, index, mode, entry_split_to_columns_entry=self.entry_split_to_columns_entry: self.entry_update_split_ncol())
        self.entry_split_to_columns = Entry(self.frame_operations, width=20, textvariable=self.entry_split_to_columns_entry, validate="key", validatecommand=(entry_validation_positive_numbers_nonzero, '%P'))

        # Buttons
        self.button_choose_file = Button(self.frame_file, text="File", command=lambda: self.choose_file(), pady=0, width=10, fg='blue')
        self.button_load = Button(self.frame_file, text="Load File", fg='green', command=self.load_file, pady=0, width=10)
        self.button_open_folder = Button(self.frame_file, text="Open Folder", command=lambda: self.open_folder(), pady=0, width=10)
        # self.button_undo = Button(self.frame_file, text="Undo", command=lambda: self.undo_move_files_to_folders(self.folders_created_fullpath), pady=0, width=10)
        self.button_save = Button(self.frame_file, text="Save", fg='green', command=self.save, pady=0, width=10)
        self.button_exit = Button(self.frame_file, text="Exit", fg='red', command=self.quit_program, pady=0, width=10)

        self.button_replace = Button(self.frame_operations, text="Replace", command=lambda: self.replace_text_list(self.user_entry.replace_original, self.user_entry.replace_new), pady=0, width=14, fg='blue')
        self.button_remove_between = Button(self.frame_operations, text="Remove Between", command=lambda: self.remove_text_between_list(self.user_entry.remove_between_1, self.user_entry.remove_between_2), pady=0, width=14, fg='blue')
        self.button_remove_after = Button(self.frame_operations, text="Remove After", command=lambda: self.remove_after(self.user_entry.remove_after), pady=0, width=14, fg='blue')
        self.button_parse = Button(self.frame_operations, text="Parse", command=lambda: self.parse_list(self.user_entry.parse_delim, self.user_entry.parse_ncol), pady=0, width=14, fg='blue')
        self.button_split_to_columns = Button(self.frame_operations, text="Split to Columns", command=lambda: self.split_to_columns_list(self.user_entry.parse_ncol), pady=0, width=14, fg='blue')
        self.button_remove_blank_lines = Button(self.frame_operations, text="Remove Blanks", command=lambda: self.remove_blank_lines(), pady=0, width=14, fg='blue')

        # Textbox
        self.textbox_original = Text(self.frame_review, height=15, width=100)
        # self.textbox_original_hscroll_bar = Scrollbar(self.frame_file, orient="horizontal")
        # self.textbox_original_hscroll_bar.config(command=self.textbox_original.xview)
        # self.textbox_original.config(xscrollcommand=self.textbox_original_hscroll_bar.set)
        self.textbox_original_vscroll_bar = Scrollbar(self.frame_review, orient="vertical")
        self.textbox_original_vscroll_bar.config(command=self.textbox_original.yview)
        self.textbox_original.config(yscrollcommand=self.textbox_original_vscroll_bar.set)
        self.textbox_row_clear(self.textbox_original, 'No Files Loaded')

        self.textbox_modified = Text(self.frame_review, height=15, width=100)
        self.textbox_modified_vscroll_bar = Scrollbar(self.frame_review, orient="vertical")
        self.textbox_modified_vscroll_bar.config(command=self.textbox_modified.yview)
        self.textbox_modified.config(yscrollcommand=self.textbox_modified_vscroll_bar.set)
        self.textbox_row_clear(self.textbox_modified)

        # Radiobuttons
        self.radiobutton_marker_entry = IntVar(value=self.user_entry.marker_option)
        self.radiobutton_marker_keep = Radiobutton(self.frame_operations, text="Keep Marker",
                                                       command=self.update_radiobutton_marker_option,
                                                       variable=self.radiobutton_marker_entry,
                                                       value=MARKER_KEEP)
        self.radiobutton_marker_remove = Radiobutton(self.frame_operations, text="Remove Marker",
                                                       command=self.update_radiobutton_marker_option,
                                                       variable=self.radiobutton_marker_entry,
                                                       value=MARKER_REMOVE)

        # self.radiobutton_replace_entry = IntVar(value=self.user_entry.replace_option)
        # self.radiobutton_replace_custom = Radiobutton(self.frame_operations, text="Custom", command=self.update_radiobutton_replace_option, variable=self.radiobutton_replace_entry, value=REPLACE_CUSTOM)
        # self.radiobutton_replace_newline = Radiobutton(self.frame_operations, text="New Line", command=self.update_radiobutton_replace_option, variable=self.radiobutton_replace_entry, value=REPLACE_NEWLINE)

        # Grids
        self.textbox_original.grid(row=0, column=0)
        self.textbox_modified.grid(row=1, column=0)

        self.button_replace.grid                (row=2, column=0, sticky=NE)
        self.entry_replace_original.grid        (row=2, column=1, sticky=NW, padx=(5, 0))
        label_replace.grid                      (row=2, column=1, sticky=NW, padx=(135, 0))
        self.entry_replace_new.grid             (row=2, column=1, sticky=NW, padx=(170, 0))
        # self.radiobutton_replace_custom.grid    (row=3, column=0, padx=(200, 0))
        # self.radiobutton_replace_newline.grid   (row=3, column=1, padx=(200, 0))
        self.button_remove_between.grid         (row=4, column=0, sticky=NE)
        self.entry_remove_between_1.grid        (row=4, column=1, sticky=NW, padx=(5, 0))
        label_remove_between.grid               (row=4, column=1, sticky=NW, padx=(135, 0))
        self.entry_remove_between_2.grid        (row=4, column=1, sticky=NW, padx=(170, 0))
        self.button_remove_after.grid           (row=5, column=0, sticky=NE)
        self.entry_remove_after.grid            (row=5, column=1, sticky=NW, padx=(5, 0))
        self.radiobutton_marker_keep.grid       (row=5, column=1, sticky=NW, padx=(85, 0))
        self.radiobutton_marker_remove.grid     (row=5, column=1, sticky=NW, padx=(180, 0))
        # self.button_parse.grid                  (row=7, column=0, sticky=NE)
        # label_parse_delim.grid                  (row=7, column=1, sticky=NW, padx=(5, 0))
        # self.entry_parse_delim.grid             (row=7, column=1, sticky=NW, padx=(62, 0))
        # label_parse_ncol.grid                   (row=7, column=1, sticky=NW, padx=(150, 0))
        # self.entry_parse_ncol.grid              (row=7, column=1, sticky=NW, padx=(208, 0))
        self.button_remove_blank_lines.grid     (row=8, column=0, sticky=NE)
        self.button_split_to_columns.grid       (row=9, column=0, sticky=NE)
        self.entry_split_to_columns.grid        (row=9, column=1, sticky=NW, padx=(5, 0))

        self.button_choose_file.grid(row=0, column=0, sticky=NW)
        self.entry_file_address.grid(row=0, column=0, sticky=NW, padx=(80, 0), pady=(2, 2))

        self.button_load.grid           (row=1, column=0, sticky=NW, padx=(0, 0))
        self.button_open_folder.grid    (row=1, column=0, sticky=NW, padx=(80, 0))
        self.button_save.grid           (row=1, column=0, sticky=NW, padx=(160, 0))
        self.button_exit.grid           (row=1, column=0, sticky=NW, padx=(240, 0))

        self.button_parse.config(state="disabled")

        # END OF FRAME #######################################################

        self.root_frame.mainloop()

    ######################################################################

    def set_state(self, widget, state):
        print(type(widget))
        try:
            widget.configure(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self.set_state(child, state=state)

    @staticmethod
    def quit_program():
        # quit()  # quit() does not work with pyinstaller, use sys.exit()
        sys.exit()

    def load_file(self):
        self.files_to_process = []
        self.files_moved_fullpath = []
        self.folders_created_fullpath = []
        self.bad_undo_folder = {}

        # Scan Folder
        result = self.scan_files_in_folder()

        # No Files
        if result == 0:
            message = "No Files to Process .. Process will terminate" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            return

        # No Folder
        elif result == -1:
            message = "Folder path does not exist .. Process will terminate" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            print(message)
            return

        # Files Detected
        else:
            self.user_entry.folder_path, self.user_entry.file_name, self.user_entry.file_extension = fm.FileNameMethods.split_file_full_name(self.user_entry.file_address)
            print("::user_entry.folder_path: ", self.user_entry.folder_path)
            print("::user_entry.file_name: ", self.user_entry.file_name)
            print("::user_entry.file_extension: ", self.user_entry.file_extension)
            self.file_contents_raw = self.read_text_file(self.user_entry.file_address)
            self.file_contents_raw_list = self.read_text_file_lines_stripline(self.user_entry.file_address)
            self.file_contents_modified_list = self.file_contents_raw_list

            print(self.file_contents_modified_list)
            print(len(self.file_contents_modified_list))
            # [print(item) for item in self.file_contents_modified_list]

            message = "Reading File\n"
            colour = 'green'
            self.session_log.write_textbox(message, colour)
            self.textbox_row_clear(self.textbox_original)
            self.textbox_row_clear(self.textbox_modified)
            self.textbox_update(self.textbox_original, self.file_contents_raw)
            self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def save(self):
        try:
            self.user_entry.file_new_name = self.user_entry.file_name + self.user_entry.file_new_name_append
            self.user_entry.file_new_extension = FILE_NEW_EXTENSION
            self.user_entry.file_new_folder = self.user_entry.folder_path + "/output_files"
            self.user_entry.file_new_address = fm.FileNameMethods.build_file_name_full(self.user_entry.file_new_folder, self.user_entry.file_new_name, self.user_entry.file_new_extension)
            print("::user_entry.file_new_name: ", self.user_entry.file_new_name)
            print("::user_entry.file_new_extension: ", self.user_entry.file_new_extension)
            print("::user_entry.file_new_address: ", self.user_entry.file_new_address)
            print("::user_entry.file_new_folder: ", self.user_entry.file_new_folder)

            temp_path = os.path.realpath(self.user_entry.file_new_folder)
            try:
                os.startfile(temp_path)
            except:
                try:
                    os.mkdir(self.user_entry.file_new_folder)
                    self.user_entry.file_location = self.user_entry.file_new_folder
                    self.session_log.write_textbox("Folder Created", "blue")
                    print("Folder Created")
                except OSError as e:
                    print("Failed to Create Folder")
                    e = Exception("Failed to Create Folder")
                    self.session_log.write_textbox(str(e), "red")
                    raise e

            ret = self.save_list_to_file(self.user_entry.file_new_folder, self.user_entry.file_new_name, self.file_contents_modified_list)
            if ret == 1:
                path = self.user_entry.file_new_folder + "\\" + self.user_entry.file_new_name
                print(f'Data saved to text file: {path}')
            elif ret == 0:
                print(f"Failed to write text file")

            ret = self.save_list_to_csv(self.user_entry.file_new_folder, self.user_entry.file_new_name, self.file_contents_modified_list)
            if ret == 1:
                path = self.user_entry.file_new_folder + "\\" + self.user_entry.file_new_name
                print(f'Data saved to csv file: {path}')
            elif ret == 0:
                print(f"Failed to write csv file")

        except Exception as e:
            print(f'An error occurred: {str(e)}')

    def scan_files_in_folder(self):
        message = "Scanning Folder" + '\n'
        colour = "black"
        self.session_log.write_textbox(message, colour)

        file_path = self.user_entry.file_address
        folder_path = self.user_entry.folder_path

        # Check if folder path exists
        if not fm.FileNameMethods.check_file_location_valid(folder_path):
            return -1

        # Check if file exists
        elif not fm.FileNameMethods.check_filename_full_exists(file_path):
            return 0

        else:
            return 1

    def open_folder(self):
        file_path = self.user_entry.folder_path
        if os.path.exists(file_path) and os.path.isdir(file_path):
            os.startfile(self.user_entry.folder_path)
        else:
            messagebox.showinfo(title="Error", message="Folder Does Not Exist")
            self.user_entry.file_address = FOLDER_PATH
        return

    def choose_file(self):
        # filetypes = (("Text Files", "*.txt"), ("Word Documents", "*.doc *.docx"), ("All Files", "*.*"))
        filetypes = (("Text Files", "*.txt"), ("Word Documents", "*.doc *.docx"))
        self.user_entry.file_address = filedialog.askopenfilename(initialdir=FOLDER_PATH, filetypes=filetypes)
        self.user_entry.folder_path = os.path.dirname(self.user_entry.file_address)
        self.update_entry_file_address(self.user_entry.file_address)

        message = 'File: ' + self.user_entry.file_address + '\n'
        colour = "blue"
        self.session_log.write_textbox(message, colour)
        print("::user_entry.file_address: ", self.user_entry.file_address)
        print("::user_entry.folder_path: ", self.user_entry.folder_path)

    def update_entry_file_address(self, string):
        self.entry_file_address.delete(0, END)
        self.entry_file_address.insert(0, string)

    def entry_update_file_address(self):
        file_address = self.entry_file_address_entry.get()

        if fm.FileNameMethods.check_filename_full_exists(file_address):
            self.user_entry.file_address = file_address

        else:
            self.user_entry.file_address = FILE_ADDRESS
        message = 'File Address: ' + os.path.normcase(self.user_entry.file_address) + '\n'
        colour = 'blue'
        self.session_log.write_textbox(message, colour)
        print("::user_entry.file_address : ", self.user_entry.file_address)

    def entry_update_replace_original(self):
        try:
            replace_original = self.entry_replace_original_entry.get()
            self.user_entry.replace_original = replace_original
            print("::user_entry.replace_original: ", self.user_entry.replace_original)
        except:
            self.user_entry.replace_original = REPLACE_ORIGINAL
            print("::user_entry.replace_original: ", self.user_entry.replace_original)

    def entry_update_replace_new(self):
        try:
            replace_new = self.entry_replace_new_entry.get()
            self.user_entry.replace_new = replace_new
            print("::user_entry.replace_new: ", self.user_entry.replace_new)
        except:
            self.user_entry.replace_new = REPLACE_NEW
            print("::user_entry.replace_new: ", self.user_entry.replace_new)

    def entry_update_remove_between_1(self):
        try:
            string1 = self.entry_remove_between_1_entry.get()
            self.user_entry.remove_between_1 = string1
            print("::user_entry.remove_between_1: ", self.user_entry.remove_between_1)
        except:
            self.user_entry.remove_between_1 = REMOVE_BETWEEN_1
            print("::user_entry.remove_between_1: ", self.user_entry.remove_between_1)

    def entry_update_remove_between_2(self):
        try:
            string2 = self.entry_remove_between_2_entry.get()
            self.user_entry.remove_between_2 = string2
            print("::user_entry.remove_between_2: ", self.user_entry.remove_between_2)
        except:
            self.user_entry.remove_between_2 = REMOVE_BETWEEN_2
            print("::user_entry.remove_between_2: ", self.user_entry.remove_between_2)

    def entry_update_remove_after(self):
        try:
            string = self.entry_remove_after_entry.get()
            self.user_entry.remove_after = string
            print("::user_entry.remove_after: ", self.user_entry.remove_after)
        except:
            self.user_entry.remove_after = REMOVE_AFTER
            print("::user_entry.remove_after: ", self.user_entry.remove_after)

    def entry_update_parse_delim(self):
        try:
            parse_delim = self.entry_parse_delim_entry.get()
            self.user_entry.parse_delim = parse_delim
            print("::user_entry.parse_delim: ", self.user_entry.parse_delim)
        except:
            self.user_entry.parse_delim = PARSE_DELIM
            print("::user_entry.parse_delim: ", self.user_entry.parse_delim)

    def entry_update_parse_ncol(self):
        try:
            parse_ncol = self.entry_parse_ncol_entry.get()
            self.user_entry.parse_ncol = int(parse_ncol)
            print("::user_entry.parse_ncol: ", self.user_entry.parse_ncol)
        except:
            self.user_entry.parse_ncol = PARSE_NCOL
            print("::user_entry.parse_ncol: ", self.user_entry.parse_ncol)

    def entry_update_split_ncol(self):
        try:
            split_ncol = self.entry_split_to_columns_entry.get()
            self.user_entry.split_ncol = int(split_ncol)
            print("::user_entry.split_ncol: ", self.user_entry.split_ncol)
        except:
            self.user_entry.parse_ncol = PARSE_NCOL
            print("::user_entry.parse_ncol: ", self.user_entry.parse_ncol)

    @staticmethod
    def read_text_file(file_path):
        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()
            return file_contents
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def read_text_file_lines(file_path):
        try:
            with open(file_path, 'r') as file:
                file_contents = file.readlines()
            return file_contents
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def read_text_file_lines_stripline(file_path):
        try:
            with open(file_path, 'r') as file:
                lines = [line.rstrip() for line in file.readlines()]
            return lines
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def textbox_row_clear(*args):
        if len(args) == 1:
            textbox_handle = args[0]
            message = ""
        elif len(args) == 2:
            textbox_handle, message = args

        textbox_handle.configure(state='normal')
        textbox_handle.delete('1.0', 'end')
        textbox_handle.insert('end', message)
        textbox_handle.configure(state='disabled')

    @staticmethod
    def textbox_update(textbox_handle, data):
        textbox_handle.configure(state='normal')
        textbox_handle.delete('1.0', 'end')
        textbox_handle.insert('end', data)
        textbox_handle.configure(state='disabled')

    @staticmethod
    def textbox_update_list(textbox_handle, data):
        textbox_handle.configure(state='normal')
        textbox_handle.delete('1.0', 'end')

        for item in data:
            textbox_handle.insert('end', item)
            textbox_handle.insert('end', '\n')

        textbox_handle.configure(state='disabled')

    def update_radiobutton_marker_option(self):
        radiobutton_marker_option = self.radiobutton_marker_entry.get()
        self.user_entry.marker_option = radiobutton_marker_option
        print("::user_entry.marker_option: ", self.user_entry.marker_option)

    # Replace string with another
    def replace_text_list(self, string_original, string_new):
        try:
            if string_original == "":
                print("Invalid Entry")
                return

            self.file_contents_modified_list = [string.replace(string_original, string_new) for string in self.file_contents_modified_list]
            self.textbox_update(self.textbox_original, self.file_contents_raw)
            self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

        except Exception as e:
            print(f'Invalid entry: {str(e)}')

    def remove_blank_lines(self):
        new_list = []
        for i in range(len(self.file_contents_modified_list)):
            if self.file_contents_modified_list[i] == "":
                continue
            else:
                new_list.append(self.file_contents_modified_list[i])
        self.file_contents_modified_list = new_list
        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def remove_text_between_list(self, substring1, substring2):
        if substring1 == "" or substring2 == "":
            print("Invalid Entry")
            return

        new_list = []
        for i in range(len(self.file_contents_modified_list)):
            line = self.file_contents_modified_list[i]
            start_index = line.find(substring1)
            end_index = line.find(substring2)
            if start_index == -1 or end_index == -1:
                new_list.append(line)
                continue
            new_line = line[0:start_index] + line[end_index+1:]
            # if new_line != "\n":
            if new_line != "":
                new_list.append(new_line)

        self.file_contents_modified_list = new_list
        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def remove_after(self, substring):
        if substring == "":
            print("Invalid Entry")
            return

        if self.user_entry.marker_option is MARKER_KEEP:
            self.remove_after_keep_marker_list(substring)
        elif self.user_entry.marker_option is MARKER_REMOVE:
            self.remove_after_remove_marker_list(substring)

    def remove_after_keep_marker_list(self, substring):
        new_list = []
        # print(len(self.file_contents_modified_list))
        for i in range(len(self.file_contents_modified_list)):
            if substring in self.file_contents_modified_list[i]:
                # Find index of substring
                index = self.file_contents_modified_list[i].index(substring)
                # Truncate string
                new_list.append(self.file_contents_modified_list[i][:index + len(substring)])
            else:
                new_list.append(self.file_contents_modified_list[i])
        self.file_contents_modified_list = new_list
        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def remove_after_remove_marker_list(self, substring):
        new_list = []
        for i in range(len(self.file_contents_modified_list)):
            if substring in self.file_contents_modified_list[i]:
                # Find index of substring
                index = self.file_contents_modified_list[i].index(substring)
                # Truncate string
                new_line = self.file_contents_modified_list[i][:index]
                if new_line != "":
                    new_list.append(new_line)
            else:
                new_list.append(self.file_contents_modified_list[i])
        self.file_contents_modified_list = new_list
        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def parse(self, delimiter, num_columns):
        try:
            # Split the input string using the specified delimiter
            parts = self.file_contents_modified.split(delimiter)

            # Check if the number of columns matches the specified number
            if len(parts) != num_columns:
                raise ValueError(f"Expected {num_columns} columns, but found {len(parts)}")

            self.file_contents_modified = parts

            self.textbox_update(self.textbox_original, self.file_contents_raw)
            self.textbox_update(self.textbox_modified, self.file_contents_modified)

        except ValueError as e:
            return str(e)  # Return an error message if the number of columns doesn't match

    def split_to_columns(self, ncol):
        # try:
        #     # Split the input string into columns using the column_delimiter
        #     columns = self.file_contents_modified.split(ncol)
        #
        #     self.textbox_update(self.textbox_original, self.file_contents_raw)
        #     self.textbox_update(self.textbox_modified, self.file_contents_modified)
        #
        #     return columns
        # except Exception as e:
        #     return str(e)

        # try:
        #     # Split the input string into rows
        #     rows = self.file_contents_modified.split('\n')
        #     # Initialize an empty list to store the columns
        #     columns = []
        #     # Iterate through the rows and split each row into columns
        #     for row in rows:
        #         columns.extend(row.split(None, ncol - 1))
        #
        #     self.file_contents_modified = columns
        #     # self.file_contents_modified = ",".join(columns)
        #
        #     self.textbox_update(self.textbox_original, self.file_contents_raw)
        #     self.textbox_update(self.textbox_modified, self.file_contents_modified)
        #     print(self.file_contents_modified)
        #
        #     return columns
        # except Exception as e:
        #     return str(e)

        try:
            # Split the input string into rows
            rows = self.file_contents_modified.split('\n')

            # Initialize an empty list to store the columns
            columns = []

            # Iterate through the rows and split them into columns
            for i in range(0, len(rows), ncol):
                columns.append('\n'.join(rows[i:i + ncol]))

            # Join the columns back into a single string
            # result_string = '\n'.join(columns)

            self.file_contents_modified = columns
            self.textbox_update(self.textbox_original, self.file_contents_raw)
            self.textbox_update(self.textbox_modified, self.file_contents_modified)
            print(self.file_contents_modified)

        except Exception as e:
            return str(e)

    def parse_list(self, delimiter, num_columns):
        # Check if the number of columns is valid
        if num_columns < 1:
            raise ValueError("Number of columns must be greater than or equal to 1")

        # Initialize the output list as a list of empty lists
        output_list = [[] for _ in range(num_columns)]

        # Split the input list into columns
        for index, item in enumerate(self.file_contents_modified_list):
            column_index = index % num_columns
            output_list[column_index].append(item)

        # Join each column using the delimiter and return the result
        result_list = [delimiter.join(column) for column in output_list]

        self.file_contents_modified_list = result_list
        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    def split_to_columns_list(self, ncol):
        if ncol <= 0:
            raise ValueError("Number of columns must be greater than zero.")

        # Calculate the number of rows required
        num_rows = len(self.file_contents_modified_list) // ncol + (len(self.file_contents_modified_list) % ncol > 0)

        # Initialize a 2D list to hold the rearranged data
        rearranged_list = [[] for _ in range(num_rows)]

        # Fill the 2D list with data from the input list
        for i, item in enumerate(self.file_contents_modified_list):
            row = i // ncol
            rearranged_list[row].append(item)

        self.file_contents_modified_list = rearranged_list

        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update_list(self.textbox_modified, self.file_contents_modified_list)

    @staticmethod
    def save_list_to_file(file_folder, file_name, input_list):
        try:
            # Open file in write mode
            file_path = file_folder + '\\' + file_name + '.txt'
            with open(file_path, 'w') as file:
                # Write each list element to file
                for item in input_list:
                    file.write(str(item) + '\n')
            return 1
        except Exception as e:
            print(f'Error: {str(e)}')
            return 0

    @staticmethod
    def save_list_to_csv(file_folder, file_name, input_list):
        try:
            file_path = file_folder + '\\' + file_name + '.csv'
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                for row in input_list:
                    writer.writerow(row)
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 0
