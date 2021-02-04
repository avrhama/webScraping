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
class linkedinModel:
	def __init__(self,addFilterJob,scanJobsFinished):
		self.addFilterJob=addFilterJob
		self.scanJobsFinished=scanJobsFinished
		self.headers={
		'Host':'www.linkedin.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
		'Accept':'*/*',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		#'Csrf-Token':'ajax:2836671000495482845',
		'Connection':'keep-alive',
		'Referer':'https://www.linkedin.com/company/linkedin/jobs',
		'Pragma':'no-cache',
		'Cache-Control':'no-cache',
		'TE':'Trailers'
		}
		self.s=requests.session()
	
	def stopScanJobs(self):
		self.keepScaning=False
	def scanJobs(self,jobTitle,cityName):
		print("scaning linkedin...")
		s=self.s
		headers=self.headers
		cityName=urllib.parse.quote(cityName)
		cityInfoURL='https://www.linkedin.com/organization-guest/api/typeaheadHits?query={}&typeaheadType=GEO&geoTypes=POPULATED_PLACE,ADMIN_DIVISION_2,MARKET_AREA,COUNTRY_REGION'.format(cityName)
		response=s.get(cityInfoURL,headers=headers)
		response=json.loads(response.text)
		if not response:
			print("cant find the city:",cityName)
			return
		jobTitle=jobTitle.replace(' ','+')
		cityID=response[0]['id']
		cityName=urllib.parse.quote(response[0]['displayName'])
		url="https://www.linkedin.com/jobs/search?f_TP=1%2C2%2C3%2C4&keywords={}&location={}&geoId={}&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0".format(jobTitle,cityName,cityID)
		#
		urlPattern=url+"&start={}"
		response=s.get(url,headers=headers,allow_redirects=False)
		start=25
		self.keepScaning=True
		while self.keepScaning:

			sourceSoup = BeautifulSoup(response.text,features="lxml")
			if not sourceSoup.body:
				self.scanJobsFinished()
				break
			jobsElements=sourceSoup.body.find_all('li', attrs={'class': 'result-card'})			
			jobs=[]
			try:
				print(jobsElements[0].attrs['data-id']+'linkedin')
				for jobEle in jobsElements:			
						jobId=jobEle.attrs['data-id']+'linkedin'
						jobLinkEle=jobEle.find('a',attrs={'class':'result-card__full-card-link'})
						jobLink=jobLinkEle.attrs['href']
						jobTitle=jobLinkEle.contents[0].text
						jobLocation=jobEle.find('span',attrs={'class':'job-result-card__location'}).text
						added=jobEle.find('time').attrs['datetime']
						d = datetime.strptime(added, '%Y-%m-%d')
						timestamp = datetime.timestamp(d)				
						job={'jobID':jobId,'site':'linkedin','jobTitle':jobTitle,'jobLocation':jobLocation,'jobLink':jobLink,'added':timestamp}
						jobs.append(job)
			except:
				traceback.print_exc()
			self.filterJobs(jobs)
			if self.keepScaning:
				print("getting page:",start//25+1)
				response=s.get(urlPattern.format(start),headers=headers,allow_redirects=False)
			start+=25

		print('linkedin scan finished!')
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
				jobDescription=sourceSoup.body.find('section', attrs={'class': 'description'}).text.lower()
				jobTitle=job['jobTitle'].lower()
				ans=jobFilter.check(jobTitle,jobDescription)
				if ans:
					self.addFilterJob(job)
			except:
				traceback.print_exc()
