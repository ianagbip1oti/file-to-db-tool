from tkinter import Tk

from tool.connect_database_window import ConnectDatabaseWindow

if __name__ == '__main__':
	root = Tk()
	connect_db = ConnectDatabaseWindow(root)
	root.mainloop()
