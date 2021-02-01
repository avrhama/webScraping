from basicDataBase import DataBase
import threading
from datetime import datetime, timedelta
class jobDBModel:
	def __init__(self,dbPath):
		self.db=DataBase(dbPath)
		self.dbLock=threading.Lock()
		self.expiredJobsDays=30
	def insertJob(self,job):
		self.dbLock.acquire()
		self.db.connect()
		where='jobID="{}"'.format(job['jobID'])
		exists=self.db.exists('jobsTbl',where)
		if not exists:
			fields='jobID,site,jobTitle,jobLocation,jobLink,added'
			values='"{}","{}","{}","{}","{}",{}'.format(job['jobID'],job['site'],job['jobTitle'],job['jobLocation'],job['jobLink'],job['added'])
			self.db.insert('jobsTbl',fields,values)
		self.db.close()
		self.dbLock.release()
		return exists
	def deleteExpiredJobs(self):
		self.dbLock.acquire()
		self.db.connect()
		expiredDate = datetime.timestamp(datetime.today() - timedelta(days=self.expiredJobsDays))
		self.db.delete('jobsTbl','added < {}'.format(expiredDate))
		self.db.close()
		self.dbLock.release()
	def selectJob(self,jobID):
		self.dbLock.acquire()
		self.db.connect()
		where='jobID="{}"'.format(jobID)
		records=self.db.select('jobsTbl','jobID,site,jobTitle,jobLocation,jobLink,added',where)
		self.db.close()
		self.dbLock.release()

		if records:
			record=records[0]
			job={'jobID':record[0],'site':record[1],'jobTitle':record[2],'jobLocation':record[3],'jobLink':record[4],'added':record[5]}
			return job
	def appliedJob(self,jobID):
		self.deleteExpiredJobs()
		self.dbLock.acquire()
		self.db.connect()
		where='jobID="{}"'.format(jobID)
		self.db.update('jobsTbl','applied=1',where)
		self.db.close()
		self.dbLock.release()		
	def selectAllNotAppliedJobs(self):
		self.dbLock.acquire()
		self.db.connect()
		where='applied=0'
		records=self.db.select('jobsTbl','jobID,site,jobTitle,jobLocation,jobLink,added',where)
		self.db.close()
		self.dbLock.release()
		jobs=[]
		for record in records:
				job={'jobID':record[0],'site':record[1],'jobTitle':record[2],'jobLocation':record[3],'jobLink':record[4],'added':record[5]}
				jobs.append(job)
		return jobs

def testInsert(jdm):
	d = datetime.today() - timedelta(days=20)
	timestamp = datetime.timestamp(d)
	job={'jobID':'1234','site':'glassdoor','jobTitle':'QA','jobLink':'aliceANDbob','jobLocation':'tel aviv','added':timestamp}
	jdm.insertJob(job)
def testDelete(jdm):
	jdm.deleteExpiredJobs()
def testSelect(jdm):
	job=jdm.selectJob('1234')
	print(job)
#jdm=jobDBModel('jobsDB.sqlite')
#testInsert(jdm)
#testDelete(jdm)
#testSelect(jdm)
