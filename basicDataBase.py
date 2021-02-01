import sqlite3,datetime,re,traceback
class DataBase:
	def __init__(self,databasePath):
		self.databasePath=databasePath
		
	def connect(self):
		self.conn = sqlite3.connect(self.databasePath)
		self.c = self.conn.cursor()
		
	def close(self):
		self.conn.close()
		
	def insert(self,table,fields,values):
		try:

			self.c.execute("INSERT INTO {} ({}) VALUES ({})".format(table, fields, values))
			self.conn.commit()
			return self.c.lastrowid
		except Exception as e:
			print(e)
			traceback.print_exc()
			print("INSERT INTO {} ({}) VALUES ({})".format(table, fields, values))
			
	def selectAll(self,table):
		try:
			self.c.execute('SELECT * FROM {}'.format(table))
			return self.c.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()
    
	def selectAllLike(self,table,like):
		try:		
			self.c.execute('SELECT * FROM {} WHERE {}'.format(table,like))
			return self.c.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()
			
	def select(self,table,fields ,where):
		try:
			self.c.execute('SELECT {} FROM {} WHERE {}'.format(fields ,table,where))
			return self.c.fetchall()
		except Exception as e:
			print(e)
			traceback.print_exc()
	def update(self,table,set,where):
		try:
			self.c.execute("UPDATE {} SET {} WHERE {}".format(table, set,where))
			self.conn.commit()
		except Exception as e:
			print(e)
			traceback.print_exc()
	def exists(self,table,where):
		try:
			self.c.execute("SELECT COUNT(1) FROM {} WHERE {}".format(table,where))
			count=self.c.fetchall()
			return count[0][0]!=0
		except Exception as e:
			print(e)
			traceback.print_exc()
	def delete(self,table,where):
		try:
			self.c.execute('DELETE  FROM {} WHERE {}'.format(table,where))
			self.conn.commit()
		except Exception as e:
			print(e)