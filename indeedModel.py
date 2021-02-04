from importlib import import_module
import sys
from bs4 import BeautifulSoup
import requests,json
from datetime import datetime, timedelta
from time import sleep
import urllib.parse
import traceback
def dynamic_import(abs_module_path, class_name):
	module_object = import_module(abs_module_path)
	target_class = getattr(module_object, class_name)
	return target_class	
def importScript(package):
	if package in sys.modules:
		del sys.modules[package]
	return dynamic_import(package,package)()
class indeedModel:
	def __init__(self,addFilterJob,scanJobsFinished):
		self.addFilterJob=addFilterJob
		self.scanJobsFinished=scanJobsFinished
		self.headers={
		'Host':'il.indeed.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		#'Referer':'https://il.indeed.com/jobs?q=junior&l=netanya',
		'Connection':'keep-alive',
		'Upgrade-Insecure-Requests':'1',
		'Pragma':'no-cache',
		'Cache-Control':'no-cache',
		'TE':'Trailers'
		}
		self.s=requests.session()
	
	def stopScanJobs(self):
		self.keepScaning=False
	def scanJobs(self,jobTitle,cityName):
		print("scaning indeed...")
		s=self.s
		headers=self.headers
		cityName=urllib.parse.quote(cityName)
		cityInfoURL="https://autocomplete.indeed.com/api/v0/suggestions/location?country=IL&language=iw&count=10&formatted=1&query={}&useEachWord=false&showAlternateSuggestions=false".format(cityName)
		response=s.get(cityInfoURL)
		response=json.loads(response.text)
		if not response:
			print("cant find the city:",cityName)
			return
		cityName=urllib.parse.quote(response[0]['suggestion'])
		jobTitle=jobTitle.replace(' ','+')
		urlPattern="https://il.indeed.com/jobs?sort=date&q={}&l={}&start=".format(jobTitle,cityName)+"{}"
		start=0
		self.keepScaning=True
		todayDate=datetime.today()
		while self.keepScaning:
			print("getting page:",start//10+1)
			url=urlPattern.format(start)
			start+=10
			self.headers['Referer']=url
			response=s.get(url,headers=headers,allow_redirects=False)
			sourceSoup = BeautifulSoup(response.text,features="lxml")
			if not sourceSoup.body:
				self.scanJobsFinished()
				break
			jobsElements=sourceSoup.body.find_all('div', attrs={'class': 'jobsearch-SerpJobCard'})			
			jobs=[]
			print(len(jobsElements))
			try:			
				for jobEle in jobsElements:								
						jobId=jobEle.attrs['id']+'indded'
						jobLinkEle=jobEle.find('a',attrs={'class':'jobtitle'})
						jobLink='https://il.indeed.com'+jobLinkEle.attrs['href']
						jobTitle=jobLinkEle.attrs['title']
						jobLocation=jobEle.find(attrs={'class':'location'}).text

						added=jobEle.find('span',attrs={'class':'date'}).text
						daysPassed=self.getDaysPassed(added)
						d = todayDate - timedelta(days=daysPassed)
						timestamp = datetime.timestamp(d)
						job={'jobID':jobId,'site':'linkedin','jobTitle':jobTitle,'jobLocation':jobLocation,'jobLink':jobLink,'added':timestamp}				
						jobs.append(job)
			except :
				traceback.print_exc()
			self.filterJobs(jobs)
			navigationEle=sourceSoup.body.find_all('ul', attrs={'class': 'pagination-list'})
			if not navigationEle:
				self.keepScaning=False
			else:
				lastnpEleLabel=navigationEle[0].contents[-1].contents[0].attrs['aria-label']
				if lastnpEleLabel!='הבא':
					self.keepScaning=False				
			

		print('indeed scan finished!')
		self.scanJobsFinished()

	
	def filterJobs(self,jobs):
		s=self.s
		headers=self.headers
		#dynamically import, I can improve/fix the module on fly.
		jobFilter=importScript('jobsFilter')
		goodJobs=[]
		for job in jobs:
			if not self.keepScaning:
				break
			try:
				jobLink=job['jobLink']
				site=s.get(jobLink,headers=headers)
				sourceSoup = BeautifulSoup(site.text,features="lxml")
				jobDescription=sourceSoup.body.find(attrs={'id': 'jobDescriptionText'}).text.lower()
				jobTitle=job['jobTitle'].lower()
				ans=jobFilter.check(jobTitle,jobDescription)
				if ans:
					self.addFilterJob(job)
			except :
				traceback.print_exc()
	def getDaysPassed(self,added):
		if added=='פורסם זה עתה' or 'היום'==added:
			return 0
		added=added.replace('+','')
		days= [int(s) for s in added.split() if s.isdigit()]
		return days[0]


