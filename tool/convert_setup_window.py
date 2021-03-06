from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

import pandas as pd
from pandas import DataFrame

from tool import utils
from tool.db_tool import DatabaseTool
from tool.settings import Settings


# TODO: Fix the table name field and label not being on the same line
# TODO: Allow users to change the name of the columns
# TODO: Add the resetting of the fields
class ConvertSetupWindow(Frame):
	def __init__(self, master: Tk, db_tool: DatabaseTool, filename: str,
				 skiprows: int, delimiter: str, missing_values: list,
				 fill_value: str):
		super().__init__(master=master)
		self.__filename = filename
		self.__skiprows = skiprows
		self.__delimiter = delimiter
		self.__missing_values = missing_values
		self.__fill_value = fill_value

		self.__dtypes = [
			'string', 'int64', 'float64',
			'bool', 'datetime64'
		]

		self.__master = master
		self.__tool = db_tool

		self.__df: DataFrame = self.__open_file__()
		print(self.__df.values)
		self.__config__()

	def __open_file__(self):
		df = pd.read_csv(self.__filename, skiprows=self.__skiprows, delimiter=self.__delimiter,
						 na_values=self.__missing_values)
		df = df.fillna(self.__fill_value)
		return df

	def __config__(self):
		self.pack(padx=Settings.padding_x, pady=Settings.padding_y, fill=BOTH)
		self.winfo_toplevel().title('Connected to: {}'.format(self.__tool.database))

		menu = Menu(master=self)
		menu.add_command(label='Back', command=self.__back__)
		menu.add_command(label='View Tables', command=self.__display_tables__)
		self.__master.config(menu=menu)

		# filename
		Label(master=self, text='Converting:', font=Settings.font_medium).pack(anchor=W)
		filename_str = StringVar()
		filename_str.set(self.__filename)
		filename_field = Entry(master=self, textvariable=filename_str, font=Settings.font_small, state=DISABLED)
		filename_field.pack(pady=(0, Settings.padding_y), anchor=W, fill=X)

		# table name
		tablename_frame = Frame(master=self)
		tablename_frame.pack(fill=X)
		tablename = Label(master=tablename_frame, text='Table Name:', font=Settings.font_small)
		tablename.pack(side=LEFT, padx=(0, Settings.padding_x))
		tablename_str = StringVar()
		self.__tablename_field = Entry(master=tablename_frame, textvariable=tablename_str, font=Settings.font_small)
		self.__tablename_field.pack(fill=X, pady=(0, Settings.padding_y))

		# table headers
		self.__headers = Frame(master=self)
		self.__headers.pack(fill=X)
		self.__populate_table_headers__()

		button_frame = Frame(master=self)
		button_frame.pack(anchor=E)

		# reset button
		reset_button = Button(master=button_frame, text='Reset', font=Settings.font_small,
							  command=self.__reset_fields__)
		reset_button.grid(row=0, column=0, padx=(0, Settings.padding_x))

		# convert button
		convert_button = Button(master=button_frame, text='Convert', font=Settings.font_small, command=self.__convert__)
		convert_button.grid(row=0, column=1)

	def __populate_table_headers__(self):
		self.__pks = []
		for col_name, col_type in zip(self.__df.columns.values, self.__df.dtypes):
			inline_frame = Frame(master=self.__headers)
			inline_frame.pack(fill=X, pady=(0, Settings.padding_y))

			col_name_str = StringVar()
			col_name_str.set(col_name)
			col_name_field = Entry(master=inline_frame, textvariable=col_name_str, font=Settings.font_small,
								   state=DISABLED)
			col_name_field.grid(row=0, column=0, padx=(0, Settings.padding_x))

			col_type_selection = Combobox(master=inline_frame,
										  value=self.__dtypes,
										  font=Settings.font_small,
										  state="readonly")
			col_type_selection.set(col_type if col_type != 'object' else 'string')
			col_type_selection.grid(row=0, column=1, padx=(0, Settings.padding_x))

			pk = BooleanVar()
			primary_key_check = Checkbutton(master=inline_frame, text='PK', font=Settings.font_small,
											variable=pk)
			primary_key_check.grid(row=0, column=2)
			self.__pks.append(pk)

	def __back__(self):
		utils.launch_file_selection(self.__master, self.__tool)

	def __display_tables__(self):
		tables = self.__tool.get_tables()
		to_display = '\n'.join([key for key, value in tables.items()])
		messagebox.showinfo('Existing Tables', to_display)

	def __reset_fields__(self):
		pass

	def __is_valid_pk__(self, headers: dict):
		pks = [key for key, value in headers.items() if value[1]]
		filtered = self.__df[pks[0]].map(str)

		for i in range(1, len(pks)):
			filtered += self.__df[pks[i]].map(str)

		length = len(filtered)
		d_length = len(set(filtered))

		return length == d_length

	@staticmethod
	def __check_pk__(headers: dict):
		has_pk = False
		for value in headers.values():
			has_pk |= value[1]
		return has_pk

	def __get_all_values__(self):
		rows = { }
		key = ''
		for i, row in enumerate(self.__headers.winfo_children()):
			for j, child in enumerate(row.winfo_children()):
				if j == 0 and type(child) is Entry:
					key = child.get()
					rows[key] = []
				else:
					if type(child) is Entry or type(child) is Combobox:
						print(child.get())
						rows[key].append(child.get())
					elif type(child) is Checkbutton:
						rows[key].append(self.__pks[i].get())
		return rows

	def __convert__(self):
		table_name = self.__tablename_field.get()
		if table_name.strip() == '':
			messagebox.showerror('Empty table name', 'You did not specify a table name!')
		else:
			headers = self.__get_all_values__()
			if not self.__check_pk__(headers):
				messagebox.showerror('No Primary Key', 'You did not select any primary keys')
			else:
				if not self.__is_valid_pk__(headers):
					messagebox.showerror('Invalid Primary Key',
										 'The primary key(s) you selected is invalid as there are repeating values')
				else:
					if self.__tool.has_table(table_name):
						messagebox.showerror('Table name used', 'The table name: {} is already used'.format(table_name))
					else:
						messagebox.showinfo('Converting file to table!',
											'The file: {} is currently being converted to a table!'.format(
												self.__filename))
						self.__tool.convert(self.__df, table_name, headers)
						utils.launch_file_selection(self.__master, self.__tool)
