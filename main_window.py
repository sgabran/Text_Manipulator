# 2023-9-4

import os
import os.path
from idlelib.tooltip import *
from tkinter import filedialog
from tkinter import messagebox

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
        self.file_contents_modified = ""

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

        self.button_replace = Button(self.frame_operations, text="Replace", command=lambda: self.replace_text(self.user_entry.replace_original, self.user_entry.replace_new), pady=0, width=14, fg='blue')
        self.button_remove_between = Button(self.frame_operations, text="Remove Between", command=lambda: self.remove_text_between(self.user_entry.remove_between_1, self.user_entry.remove_between_2), pady=0, width=14, fg='blue')
        self.button_remove_after = Button(self.frame_operations, text="Remove After", command=lambda: self.remove_after(self.user_entry.remove_after), pady=0, width=14, fg='blue')
        self.button_parse = Button(self.frame_operations, text="Parse", command=lambda: self.parse(self.user_entry.parse_delim, self.user_entry.parse_ncol), pady=0, width=14, fg='blue')
        self.button_split_to_columns = Button(self.frame_operations, text="Split to Columns", command=lambda: self.split_to_columns(self.user_entry.parse_ncol), pady=0, width=14, fg='blue')

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
        self.button_parse.grid                  (row=7, column=0, sticky=NE)
        label_parse_delim.grid                  (row=7, column=1, sticky=NW, padx=(5, 0))
        self.entry_parse_delim.grid             (row=7, column=1, sticky=NW, padx=(62, 0))
        label_parse_ncol.grid                   (row=7, column=1, sticky=NW, padx=(150, 0))
        self.entry_parse_ncol.grid              (row=7, column=1, sticky=NW, padx=(208, 0))
        self.button_split_to_columns.grid       (row=8, column=0, sticky=NE)
        self.entry_split_to_columns.grid        (row=8, column=1, sticky=NW, padx=(5, 0))

        self.button_choose_file.grid(row=0, column=0, sticky=NW)
        self.entry_file_address.grid(row=0, column=0, sticky=NW, padx=(80, 0), pady=(2, 2))

        self.button_load.grid           (row=1, column=0, sticky=NW, padx=(0, 0))
        self.button_open_folder.grid    (row=1, column=0, sticky=NW, padx=(80, 0))
        self.button_save.grid           (row=1, column=0, sticky=NW, padx=(160, 0))
        self.button_exit.grid           (row=1, column=0, sticky=NW, padx=(240, 0))
        # self.button_undo.grid         (row=6, column=1, sticky=NW, padx=(80, 0))

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
            self.file_contents_modified = self.file_contents_raw
            message = "Reading File\n"
            colour = 'green'
            self.session_log.write_textbox(message, colour)
            self.textbox_row_clear(self.textbox_original)
            self.textbox_row_clear(self.textbox_modified)
            self.textbox_update(self.textbox_original, self.file_contents_raw)

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

            with open(self.user_entry.file_new_address, 'w') as file:
                file.write(self.file_contents_modified)
            print(f'Successfully saved the string to {self.user_entry.file_new_address}')
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

    def create_folders_and_move_files(self, filenames_list, destination_root_folder):
        # Check if the destination folder exists
        if not os.path.exists(destination_root_folder):
            message = "Folder path does not exist .. Process will terminate" + '\n'
            colour = 'brown'
            self.session_log.write_textbox(message, colour)
            print(message)
            return -1

        for filename in filenames_list:
            # Create a folder using the filename in the destination folder
            folder_name = os.path.splitext(filename)[0]
            file_path  = os.path.join(destination_root_folder, folder_name)

            # Create the folder
            try:
                os.makedirs(file_path )
                self.folders_created_fullpath.append(file_path )
                print(f"Folder created: {file_path }")
            except FileExistsError:
                message = f"Folder already exists: {file_path }" + '\n'
                colour = 'brown'
                self.session_log.write_textbox(message, colour)
                print(message)

            # Move the file to the created folder
            try:
                file_path = os.path.join(destination_root_folder, filename)
                new_file_path = os.path.join(file_path , filename)

                if not os.path.isfile(new_file_path):
                    shutil.move(file_path, new_file_path)
                    self.files_moved_fullpath.append(new_file_path)
                    message = str(filename) + "  >>>  " + str(os.path.dirname(new_file_path)) + '\n'
                    colour = 'black'
                    self.session_log.write_textbox(message, colour)
                    print(message)

                else:
                    message = f"File {file_path} Exists and Will Be Ignored" + '\n'
                    colour = 'red'
                    self.session_log.write_textbox(message, colour)
                    print(message)

                self.n_folders_created_fullpath = len(self.folders_created_fullpath)
                self.n_files_moved_fullpath = len(self.files_moved_fullpath)

            except FileNotFoundError:
                message = f"File not found: {filename}" + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)
                print(message)

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

    def undo_move_files_to_folders(self, folders_fullpath):
        self.bad_undo_folder = {}
        self.n_restored_files = 0
        self.n_deleted_folders = 0
        self.finished_with_errors = 1

        # check if changes were done
        if self.n_folders_created_fullpath == self.n_files_moved_fullpath == 0:
            message = "Nothing to Undo" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            messagebox.showinfo(title="Warning", message=message)
            return -1

        message = "Start to Undo" + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)

        # Check folder integrity. "folder" is full pathname
        for folder_fullpath in folders_fullpath:

            # 1. Check if folder exists
            if os.path.exists(folder_fullpath) and os.path.isdir(folder_fullpath):

                # 2. Check number of folder contents: must equal to 1.
                # "folder_contents" is filename with extension
                folder_contents = os.listdir(folder_fullpath)
                if len(folder_contents) == 0:
                    # self.bad_undo_folder.append(folder_fullpath)
                    self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_2

                elif len(folder_contents) > 1:
                    # self.bad_undo_folder.append(folder_fullpath)
                    self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_3

                else:
                    # 3. Check folder contents: file must have same folder name
                    folder_name = os.path.basename(folder_fullpath)
                    filename_without_extension = os.path.splitext(os.path.basename(folder_contents[0]))[0]
                    if folder_name != filename_without_extension:
                        # self.bad_undo_folder.append(folder_fullpath)
                        self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_4

                    else:
                        filename = os.path.basename(folder_contents[0])
                        filename_original_path = os.path.join(folder_fullpath, filename)
                        file_destination_path = os.path.join(self.user_entry.file_address , filename)
                        # Move file
                        shutil.move(filename_original_path, file_destination_path)
                        message = "Moved: " + filename_original_path + " >> to >> " + file_destination_path + '\n'
                        colour = 'black'
                        self.session_log.write_textbox(message, colour)
                        self.n_restored_files += 1
                        # Delete folder
                        shutil.rmtree(folder_fullpath)
                        self.n_deleted_folders += 1
                        message = "Folder Deleted" + '\n'
                        colour = 'black'
                        self.session_log.write_textbox(message, colour)

            else:
                # self.bad_undo_folder.append(folder_fullpath)
                self.bad_undo_folder[folder_fullpath] = BAD_FOLDER_ERROR_1

        # List bad folders
        if len(self.bad_undo_folder) > 0:
            message = "Errors Found in Some Folders. Bad Folders are Ignored" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            message = "Bad Folders: " + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)

            for folder, error in self.bad_undo_folder.items():
                message = '\t' + folder + " >> " + error + '\n'
                colour = 'red'
                self.session_log.write_textbox(message, colour)

            message = "Errors Found in Some Folders" + '\n' + "Bad Folders are Ignored" + '\n'
            messagebox.showinfo(title="Error", message=message)

        else:
            self.finished_with_errors = 0

        message = "Number of Files Restored: " + str(self.n_restored_files) + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)
        message = "Number of Folder Deleted: " + str(self.n_deleted_folders) + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)

        if not self.finished_with_errors:
            message = "Process Finished Successfully" + '\n'
            colour = 'green'
            self.session_log.write_textbox(message, colour)

        else:
            message = "Process Finished with Errors" + '\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)

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

    def entry_update_rows_to_peak_raw(self):
        try:
            n_rows_to_peak_raw = self.entry_rows_to_peak_raw_entry.get()
            self.user_entry.n_rows_to_peak_raw = int(n_rows_to_peak_raw)
            print("::user_entry.n_rows_to_peak_raw: ", self.user_entry.n_rows_to_peak_raw)
        except:
            self.user_entry.data_start_row_index = N_ROWS_TO_PEAK_RAW
            print("::user_entry.n_rows_to_peak_raw: ", self.user_entry.n_rows_to_peak_raw)
        self.user_entry.n_rows_to_peak_raw = [0] * self.user_entry.n_rows_to_peak_raw

    def entry_update_rows_to_peak_modified(self):
        try:
            n_rows_to_peak_modified = self.entry_rows_to_peak_modified_entry.get()
            self.user_entry.n_rows_to_peak_modified = int(n_rows_to_peak_modified)
            print("::user_entry.n_rows_to_peak_modified: ", self.user_entry.n_rows_to_peak_modified)
        except:
            self.user_entry.data_start_row_index = N_ROWS_TO_PEAK_MODIFIED
            print("::user_entry.n_rows_to_peak_modified: ", self.user_entry.n_rows_to_peak_modified)
        self.user_entry.n_rows_to_peak_modified = [0] * self.user_entry.n_rows_to_peak_modified

    def update_radiobutton_marker_option(self):
        radiobutton_marker_option = self.radiobutton_marker_entry.get()
        self.user_entry.marker_option = radiobutton_marker_option
        print("::user_entry.marker_option: ", self.user_entry.marker_option)

    # def update_radiobutton_replace_option(self):
    #     radiobutton_replace_option = self.radiobutton_replace_entry.get()
    #     self.user_entry.replace_option = radiobutton_replace_option
    #     print("::user_entry.replace_option: ", self.user_entry.replace_option)
    #     if self.user_entry.replace_option == REPLACE_CUSTOM:
    #         self.entry_replace_original.configure(state='normal')
    #     elif self.user_entry.replace_option == REPLACE_NEWLINE:
    #         self.entry_replace_original.configure(state='disabled')

    # Replace string with another
    def replace_text(self, string_original, string_new):
        try:
            if string_original != "":
                self.file_contents_modified = self.file_contents_modified.replace(string_original, string_new)
                self.textbox_update(self.textbox_original, self.file_contents_raw)
                self.textbox_update(self.textbox_modified, self.file_contents_modified)
            else:
                print("Invalid Entry")
        except Exception as e:
            print(f'Invalid entry: {str(e)}')

    # # Replace string with another
    # def replace_text(self, string_original, string_new):
    #     try:
    #         if self.user_entry.replace_option == REPLACE_CUSTOM:
    #             self.file_contents_modified = self.file_contents_modified.replace(string_original, string_new)
    #             self.textbox_update(self.textbox_original, self.file_contents_raw)
    #             self.textbox_update(self.textbox_modified, self.file_contents_modified)
    #         elif self.user_entry.replace_option == REPLACE_NEWLINE:
    #             self.file_contents_modified = self.file_contents_modified.replace("\r\n", string_new)
    #             self.textbox_update(self.textbox_original, self.file_contents_raw)
    #             self.textbox_update(self.textbox_modified, self.file_contents_modified)
    #     except Exception as e:
    #         print(f'An error occurred: {str(e)}')

    def remove_text_between(self, substring1, substring2):
        try:
            if substring1 and substring2 != "":
                while substring1 in self.file_contents_modified and substring2 in self.file_contents_modified:
                    start_index = self.file_contents_modified.index(substring1)
                    end_index = self.file_contents_modified.index(substring2)
                    self.file_contents_modified = self.file_contents_modified[:start_index] + self.file_contents_modified[end_index + len(substring2):]

                # Remove any resulting empty lines
                lines = self.file_contents_modified.split('\n')
                cleaned_lines = [line for line in lines if line.strip()]
                self.file_contents_modified = '\n'.join(cleaned_lines)

                self.textbox_update(self.textbox_original, self.file_contents_raw)
                self.textbox_update(self.textbox_modified, self.file_contents_modified)
            else:
                print("Invalid Entry")
        except Exception as e:
            print(f'An error occurred: {str(e)}')

    def remove_after(self, substring):
        if substring != "":
            if self.user_entry.marker_option is MARKER_KEEP:
                self.remove_after_keep_marker(substring)
            elif self.user_entry.marker_option is MARKER_REMOVE:
                self.remove_after_remove_marker(substring)
        else:
            print("Invalid Entry")

    def remove_after_keep_marker(self, substring):
        # Split the original string into lines
        lines = self.file_contents_modified.split('\n')
        modified_lines = []

        for line in lines:
            if substring in line:
                index = line.index(substring)
                modified_line = line[:index + len(substring)]
            else:
                modified_line = line

            modified_lines.append(modified_line)

        # Join the modified lines back into a string
        self.file_contents_modified = '\n'.join(modified_lines)

        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update(self.textbox_modified, self.file_contents_modified)

    def remove_after_remove_marker(self, substring):
        # Split the original string into lines
        lines = self.file_contents_modified.split('\n')
        modified_lines = []

        for line in lines:
            if substring in line:
                index = line.index(substring)
                modified_line = line[:index]
            else:
                modified_line = line

            modified_lines.append(modified_line)

        # Join the modified lines back into a string and remove extra empty lines
        self.file_contents_modified = '\n'.join(modified_lines).strip()

        # Remove any resulting empty lines
        lines = self.file_contents_modified.split('\n')
        cleaned_lines = [line for line in lines if line.strip()]
        self.file_contents_modified = '\n'.join(cleaned_lines)

        self.textbox_update(self.textbox_original, self.file_contents_raw)
        self.textbox_update(self.textbox_modified, self.file_contents_modified)

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
