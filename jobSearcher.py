import tkinter as tk
from tkinter import Tk
import _thread as thread
from jobDBModel import jobDBModel
import webbrowser,threading
from glassdoorModel import glassdoorModel
class MyFirstGUI():
	def __init__(self, master):
		self.master = master
		master.geometry("900x240")
		master.title("webScanner")
		master.attributes("-topmost", True)		
		jobTitleLabl = tk.Label(root,text="Job Title:")
		jobTitleLabl.place(x=20,y=0)
		self.jobTitleTxt = tk.Text(root, height=1, width=25)
		self.jobTitleTxt.place(x=20,y=20)
		jobCityLabl = tk.Label(root,text="Job City:")
		jobCityLabl.place(x=250,y=0)
		self.jobCityTxt = tk.Text(root, height=1, width=15)
		self.jobCityTxt.place(x=250,y=20)
		self.scanBtn = tk.Button(master, text="scan", command=self.scan)
		self.scanBtn.place(x=390,y=15)
		scanResultsLbl = tk.Label(root,text="Scan Results:")
		scanResultsLbl.place(x=20,y=45)
		self.scanResultsTxt = tk.Text(master, height=10, width=50)
		self.scanResultsTxt.place(x=20,y=60)
		allfilteredJobsLbl = tk.Label(root,text="All Filtered Jobs:")
		allfilteredJobsLbl.place(x=450,y=45)
		self.allfilteredJobsListBox=tk.Listbox(master, height=10, width=60)
		self.allfilteredJobsListBox.place(x=450,y=60)
		self.openJobSiteBtn = tk.Button(master, text="Open", command=self.openJobSite)
		self.openJobSiteBtn.place(x=820,y=70)
		self.jobAppliedBtn = tk.Button(master, text="Applied", command=self.appliedJob)
		self.jobAppliedBtn.place(x=820,y=110)
		self.allFilterdJobs=[]
		self.jdm=jobDBModel('jobsDB.sqlite')
		self.loadAllFilteredJobs()
		chrome=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
		firefox="C:\\Program Files\\Mozilla Firefox\\firefox.exe"
		webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome),preferred=1)
		#webbrowser.register('firefox', None,webbrowser.BackgroundBrowser(firefox),preferred=1)
		self.allfilteredJobsListBoxLock=threading.Lock()
		self.searchModels=[glassdoorModel(self.addFilterJob,self.scanJobsFinished)]
	def addFilterJob(self,job):
		exists=self.jdm.insertJob(job)
		if not exists:
			self.allfilteredJobsListBoxLock.acquire()
			jobMsg='Location:{} Title:{}'.format(job['jobLocation'],job['jobTitle'])
			self.scanResultsTxt.insert(tk.END,jobMsg+"\n")
			self.scanResultsTxt.see(tk.END)
			jobItem='{} {}'.format(job['jobLocation'],job['jobTitle'],job['site'])
			self.allfilteredJobsListBox.insert(tk.END,jobItem)
			self.allFilterdJobs.append(job)
			self.allfilteredJobsListBoxLock.release()
	def loadAllFilteredJobs(self):
		jobs=self.jdm.selectAllNotAppliedJobs()
		if jobs:
			self.allFilterdJobs=jobs
			for job in jobs:
				jobItem='{} {}'.format(job['jobLocation'],job['jobTitle'],job['site'])
				self.allfilteredJobsListBox.insert(tk.END,jobItem)
	def scan(self):
		if self.scanBtn['text']=='scan':
			self.scanBtn['text']='stop'
			print("scanning...")
			cityName=self.jobCityTxt.get("1.0",tk.END)[:-1]
			jobTitle=self.jobTitleTxt.get("1.0",tk.END)[:-1]
			thread.start_new_thread(self.searchModels[0].scanJobs,(jobTitle,cityName))
		else:
			self.searchModels[0].stopScanJobs()
	def scanJobsFinished(self):
		self.scanBtn['text']='scan'
	def openJobSite(self):
		selection=self.allfilteredJobsListBox.curselection()
		if selection:
			jobLink=self.allFilterdJobs[selection[0]]['jobLink']
			webbrowser.get('chrome').open_new_tab(jobLink)
		else:
			print("none selected")
	def appliedJob(self):
		print("applied")
		self.allfilteredJobsListBoxLock.acquire()
		selection=self.allfilteredJobsListBox.curselection()
		if selection:
			jobID=self.allFilterdJobs[selection[0]]['jobID']
			self.jdm.appliedJob(jobID)
			self.allfilteredJobsListBox.delete(selection)
			self.allFilterdJobs.pop(selection[0])
			print("allFilterdJobs: ",len(self.allFilterdJobs),"allfilteredJobsListBox:",self.allfilteredJobsListBox.size())
		else:
			print("none selected")
		self.allfilteredJobsListBoxLock.release()
if __name__ == '__main__':
	root = Tk()
	my_gui = MyFirstGUI(root)
	root.mainloop()