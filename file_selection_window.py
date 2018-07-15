from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

from db_tool import DatabaseTool
from settings import Settings
from convert_setup_window import ConvertSetupWindow

# TODO: Check the file types and convert accordingly
# TODO: Before converting the file, allow the user to change the data types of the headers
# TODO: Check if the file is empty after the user tries to convert the file
class FileSelectionWindow(Frame):
	def __init__(self, master: Tk, db_tool: DatabaseTool):
		super().__init__(master=master)
		self.__tool = db_tool
		self.__master = master
		self.__config__()

	def __config__(self):
		self.pack(padx=Settings.padding_x, pady=Settings.padding_y, fill=BOTH)
		self.winfo_toplevel().title('Connected to: {}'.format(self.__tool.database))

		menu = Menu(self)
		menu.add_command(label='View Tables', command=self.__view_tables__)
		self.__master.config(menu=menu)

		# file name
		self.__file_name_str = StringVar()
		self.__file_name_str.set('Nothing is selected')
		self.__file_name_field = Entry(master=self, textvariable=self.__file_name_str, font=Settings.font_small,
									   state=DISABLED)
		self.__file_name_field.pack(fill='x', pady=(0, Settings.padding_y))

		button_frame = Frame(master=self)
		button_frame.pack(fill=X, pady=(Settings.padding_y, 0))

		# open file
		self.__open_file_button = Button(master=button_frame,
										 text='Open File',
										 font=Settings.font_small,
										 command=self.__open_file__)
		self.__open_file_button.pack(side=LEFT)

		# convert file
		self.__convert_button = Button(master=button_frame,
									   text='Convert',
									   font=Settings.font_small,
									   state=DISABLED,
									   command=self.__convert_file__)
		self.__convert_button.pack(side=RIGHT, padx=(Settings.padding_x, 0))

	def __view_tables__(self):
		tables = self.__tool.get_tables()
		to_display = '\n'.join([key for key, value in tables.items()])
		messagebox.showinfo('Existing Tables', to_display)

	def __toggle_states__(self, state):
		self.__convert_button.config(state=state)

	def __open_file__(self):
		previous_file = self.__file_name_field.get()

		selected_file = filedialog.askopenfilename(
			initialdir="/",
			title="Select file",
			filetypes=[("csv files", "*.csv")])

		if selected_file != '':
			self.__file_name_str.set(selected_file)
			self.__toggle_states__(NORMAL)
			self.__open_file_button.config(text='Change File')
		else:
			if previous_file == 'Nothing is selected':
				self.__toggle_states__(DISABLED)


	def __convert_file__(self):
		filename = self.__file_name_field.get()
		self.__master.destroy()
		ConvertSetupWindow(Tk(), self.__tool, filename)
