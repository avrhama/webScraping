from importlib import import_module
import sys
from bs4 import BeautifulSoup
import requests,json
from datetime import datetime, timedelta
from time import sleep
def dynamic_import(abs_module_path, class_name):
	module_object = import_module(abs_module_path)
	target_class = getattr(module_object, class_name)
	return target_class	
def importScript(package):
	if package in sys.modules:
		del sys.modules[package]
	return dynamic_import(package,package)()
class glassdoorModel:
	def __init__(self,addFilterJob,scanJobsFinished):
		self.addFilterJob=addFilterJob
		self.scanJobsFinished=scanJobsFinished
		self.headers={
		'Host':'www.glassdoor.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language':'en-US,en;q=0.5',
		'Accept-Encoding':'gzip, deflate, br',
		'Upgrade-Insecure-Requests':'1',
		'Connection':'keep-alive',
		'Pragma':'no-cache',
		'Cache-Control':'no-cache'
		}
		self.s=requests.session()
	#this version use webrowser only
	def test1(self):
		print('test start...')
		driver=self.driver
		#KeywordSearch
		url='https://www.glassdoor.com/Job/tel-aviv-yafo-junior-developer-jobs-SRCH_IL.0,13_IC2421096_KO14,30.htm'
		searchConfig={'locId':2421096,'typedKeyword':'junior+developer','city':'netanya'}
		
		url='https://www.glassdoor.com/Job/jobs,30_IP1.htm?suggestCount=0&sortBy=date_desc&suggestChosen=false&clickSource=searchBtn&typedKeyword={typedKeyword}&sc.keyword={typedKeyword}&locT=C&locId={locId}&jobType='.format(**searchConfig)
		url='https://www.glassdoor.com/Jobs/Glassdoor-Jobs-E100431.htm'
		driver.get(url)
		print("stage 1")
		keywordElement=driver.find_element_by_id('sc.keyword')
		locationElement=driver.find_element_by_id('sc.location')
		btnSearchElement=driver.find_element_by_id('HeroSearchButton')
		script='''
		arguments[0].setAttribute('value',arguments[1]);
		arguments[2].setAttribute('value',arguments[3]);
		arguments[4].click();
		'''
		oldUrl=driver.current_url
		driver.execute_script(script,keywordElement,searchConfig['typedKeyword'],locationElement,searchConfig['city'],btnSearchElement)
		print("stage 2")
		while oldUrl==driver.current_url:
			print(oldUrl)
			print(driver.current_url)
			sleep(1)
		url=driver.current_url
		oldUrl=driver.current_url
		driver.get(url+'&sortBy=date_desc')
		print("stage 3")
		while oldUrl==driver.current_url:
			sleep(1)
		url=driver.current_url
		urlPattern=url[:-21]+'_IP{}.htm?sortBy=date_desc'
		print("stage 4")
		#sleep(3)
		pageIndex=2
		keepScaning=True

		while keepScaning:
			jobsElements=driver.find_elements_by_xpath('//li[contains(@class, "react-job-listing")]')
			if not jobsElements:
				keepScaning=False
			try:
				jobs=[]
				for ele in jobsElements:
						jobId=ele.get_attribute('data-id')
						title=ele.find_element_by_xpath('div[2]/a/span').get_attribute('innerText').lower()
						added=ele.find_element_by_xpath('div[2]/div[2]/div/div[2]').get_attribute('innerText')
						jobLink=ele.find_element_by_xpath('div[1]/a').get_attribute('href')
						job={'jobID':jobId,'title':title,'added':added,'jobLink':jobLink}
						jobs.append(job)
						if added[-1]=='d' and int(added[:-1])>=30:
							keepScaning=False
							break
						#print(title,added)
			except Exception as e:
				print(e)
			self.scanJobs(jobs)
			print(len(jobsElements))
			url=urlPattern.format(pageIndex)
			print(url)
			print("get page ",pageIndex)
			if keepScaning:
				driver.get(url)
			pageIndex+=1


		print('test finished!')
	#this version use request and BeautifulSoup only
	def stopScanJobs(self):
		self.keepScaning=False
	def scanJobs(self,jobTitle,cityName):
		s=self.s
		headers=self.headers
		cityInfoURL='https://www.glassdoor.com/findPopularLocationAjax.htm?term={}&maxLocationsToReturn=1'.format(cityName)
		response=s.get(cityInfoURL,headers=headers)
		response=json.loads(response.text)
		if not response:
			print("cant find the city:",cityName)
			return
		locationID=response[0]['locationId']
		locationType=response[0]['locationType']
		jobTitle=jobTitle.replace(' ','+')
		url='https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={}&sc.keyword={}&locT={}&locId={}&jobType='.format(jobTitle,jobTitle,locationType,locationID)
		response=s.get(url,headers=headers)	
		url=response.url			
		urlPattern=url[:url.find('.htm')]+'_IP{}.htm?sortBy=date_desc'
		pageIndex=2
		self.keepScaning=True

		todayDate=datetime.today()
		while self.keepScaning:
			sourceSoup = BeautifulSoup(response.text,features="lxml")
			jobsElements=sourceSoup.body.find_all('li', attrs={'class': 'react-job-listing'})
			if not jobsElements:
				self.keepScaning=False
			try:
				jobs=[]
				for jobEle in jobsElements:
					jobId=jobEle.attrs['data-id']+'glassdoor'
					jobLocation=jobEle.attrs['data-job-loc']
					added=jobEle.find('div',attrs={'data-test':'job-age'}).text
					jobLinkEle=jobEle.find('a',attrs={'data-test':'job-link'})
					jobLink='https://www.glassdoor.com'+jobLinkEle.attrs['href']
					jobTitle=jobLinkEle.contents[0].text
					daysPassed=0
					if added[-1]=='d':
						daysPassed=int(added[:-1])
					d = todayDate - timedelta(days=daysPassed)
					timestamp = datetime.timestamp(d)
					job={'jobID':jobId,'site':'glassdoor','jobTitle':jobTitle,'jobLocation':jobLocation,'jobLink':jobLink,'added':timestamp}
					jobs.append(job)
					if added[-1]=='d' and int(added[:-1])>=30:
						self.keepScaning=False
						break
			except Exception as e:
				print(e)
			self.filterJobs(jobs)
			
			url=urlPattern.format(pageIndex)	
			if self.keepScaning:
				print("getting page:",pageIndex)
				response=s.get(urlPattern.format(pageIndex),headers=headers)
			pageIndex+=1



		print('scan finished!')
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
				jobDescription=sourceSoup.body.find('div', attrs={'id': 'JobDescriptionContainer'}).text
				jobTitle=job['jobTitle']
				ans=jobFilter.check(jobTitle,jobDescription)
				#print job details if matched
				if ans:
					self.addFilterJob(job)
					#msg='{}\nLocation:{} Title:{}\n{}\n{}'.format(100*'*',job['jobLocation'],jobTitle,jobLink,100*'*')
					#print(msg)
			except Exception as e:
				print(e)
		


#this the job html element structure, helpful to understand what and how data we can achieve.
'''
<li class="jl react-job-listing gdGrid selected" data-brandviews="BRAND:n=jsearch-job-listing:eid=2398513:jlid=3806460951" data-id="3806460951" data-adv-type="GENERAL" data-is-organic-job="false" data-ad-order-id="78823" data-sgoc-id="1011" data-is-easy-apply="false" data-normalize-job-title="Junior IT Engineer" data-job-loc="Tel Aviv-Yafo" data-job-loc-id="2421096" data-job-loc-type="C" style="" data-triggered-brandview-order="1">
   <div class="d-flex flex-column css-fbt9gv e1rrn5ka2"><a href="/partner/jobListing.htm?pos=101&amp;ao=78823&amp;s=58&amp;guid=00000177431860fc82d6e08194772433&amp;src=GD_JOB_AD&amp;t=SR&amp;vt=w&amp;uido=88A615214623A8F635474A75AECABC2B&amp;cs=1_ef2f75c8&amp;cb=1611738407289&amp;jobListingId=3806460951" rel="nofollow noopener noreferrer" target="_blank" class="jobLink" style="pointer-events: all;"><span class=" css-9ujsbx euyrj9o1"><img src="https://media.glassdoor.com/sql/2398513/lumigo-squarelogo-1560771933588.png" alt="Lumigo Logo" title="Lumigo Logo"></span></a><span class="compactStars ">5<i class="star"></i></span></div>
   <div class="d-flex flex-column pl-sm css-nq3w9f">
	  <div class="jobHeader d-flex justify-content-between align-items-start">
		 <a href="/partner/jobListing.htm?pos=101&amp;ao=78823&amp;s=58&amp;guid=00000177431860fc82d6e08194772433&amp;src=GD_JOB_AD&amp;t=SR&amp;vt=w&amp;uido=88A615214623A8F635474A75AECABC2B&amp;cs=1_ef2f75c8&amp;cb=1611738407289&amp;jobListingId=3806460951" rel="nofollow noopener noreferrer" target="_blank" class=" css-10l5u4p e1n63ojh0 jobLink" style="pointer-events: all;"><span>Lumigo</span></a>
		 <div class="saveJobWrap align-self-end d-flex flex-nowrap align-items-start">
			<span class="save-job-button-3806460951 saved nowrap" data-test="save-job">
			   <span class="SVGInline css-9th5vf">
				  <svg class="SVGInline-svg css-9th5vf-svg" style="width: 20px;height: 20px;" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
					 <path d="M20.37 4.65a5.57 5.57 0 00-7.91 0l-.46.46-.46-.46a5.57 5.57 0 00-7.91 0 5.63 5.63 0 000 7.92L12 21l8.37-8.43a5.63 5.63 0 000-7.92z" fill="currentColor" fill-rule="evenodd"></path>
				  </svg>
			   </span>
			</span>
		 </div>
	  </div>
	  <a href="/partner/jobListing.htm?pos=101&amp;ao=78823&amp;s=58&amp;guid=00000177431860fc82d6e08194772433&amp;src=GD_JOB_AD&amp;t=SR&amp;vt=w&amp;uido=88A615214623A8F635474A75AECABC2B&amp;cs=1_ef2f75c8&amp;cb=1611738407289&amp;jobListingId=3806460951" rel="nofollow noopener noreferrer" target="_blank" class="jobInfoItem jobTitle css-13w0lq6 eigr9kq1 jobLink" style="pointer-events: all;"><span>Junior Developer</span></a>
	  <div class="d-flex flex-wrap css-yytu5e e1rrn5ka1">
		 <span class="loc css-nq3w9f pr-xxsm">Tel Aviv-Yafo</span>
		 <div class="d-flex justify-content-between css-1qtdns2">
			<div class="d-flex flex-wrap-reverse css-15ja3jn css-1qtdns2">
			   <div class="d-flex flex-wrap">
				  <div class="mx-xxsm css-65p68w">
					 <div class="hotListing css-65p68w css-m9i057 css-1uov7ef" data-test="urgency-label">New</div>
				  </div>
			   </div>
			</div>
			<div data-test="job-age" class="d-flex align-items-end pl-std css-mi55ob">1d</div>
		 </div>
	  </div>
   </div>
</li>
'''