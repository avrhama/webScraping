class jobsFilter:
	def __init__(self):
		self.printFailedLine=False
	def check(self,title,jobDescription):
		engResult=self.checkInEng(title,jobDescription)
		if engResult:
			return self.checkInHeb(title,jobDescription)
		else:
			return False
	def checkInEng(self,title,jobDescription):
		#for now is very naive filter.
		experienceKeyword=['senior','experienced','team leader','analyst','specialist']
		for keyword in experienceKeyword:
			if keyword in title:
				if self.printFailedLine:
					print(title)
				return False
		lines=jobDescription.split('\n')
		for line in lines:
			if 'year' in line:
				if 'experience' in line:
					if ' 0-' in line:
						return True
					else:
						if self.printFailedLine:
							print(line)
						return False
		return True
	def checkInHeb(self,title,jobDescription):
		#for now is very naive filter.
		experienceKeyword=['בכיר','מנוסה','ראש צוות','רש"צ','רש"צ','ראש"צ','אנליסט']
		for keyword in experienceKeyword:
			if keyword in title:
				if self.printFailedLine:
					print(title)
				return False
		lines=jobDescription.split('\n')
		yearsForms=["שנ'","שנות","שנים","שנים"]
		for line in lines:
			for yearForm in yearsForms:
				if yearForm in line:
					if 'ניסיון' in line or 'נסיון' in line:
						if ' 0-' in line:
							return True
						else:
							if self.printFailedLine:
								print(line)
							return False
			if 'ש"נ':
				if ' 0-' in line:
					return True
				else:
					if self.printFailedLine:
						print(line)
					return False				
		return True    
