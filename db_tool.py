import pandas as pd
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists


class DatabaseTool:
	def __init__(self, username: str, password: str, host: str, port: str, database: str):
		self.database = database
		self.__connection_string = self.__create_connection_string__(username, password, host, port, database)
		self.__engine = None
		self.__Base = None
		self.__meta: MetaData = None

	@staticmethod
	def __create_connection_string__(username: str, password: str, host: str, port: str, database: str):
		return 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, database)

	def has_database(self):
		return database_exists(self.__connection_string)

	def open_engine(self):
		self.__engine = create_engine(self.__connection_string)
		self.__Base = declarative_base(bind=self.__engine)
		self.__meta = MetaData()

	def get_tables(self):
		meta = MetaData()
		meta.reflect(bind=self.__engine)
		tables = meta.tables
		return tables

	def convert(self, filename: str, skiprows: int, delimiter: str):
		df = pd.read_csv(filename, skiprows=skiprows, delimiter=delimiter)
		print(df)
