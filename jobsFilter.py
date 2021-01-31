import re
class jobsFilter:
    def __init__(self):
        self.name="j"
    def check(self,title,jobDescription):
        #for now is very naive filter.
        experienceKeyword=['senior','experienced']
        for keyword in experienceKeyword:
            if keyword in title:
                return False
        lines=jobDescription.split('\n')
        for line in lines:
            if 'year' in line:
                if 'experience' in line:
                    if ' 0-' in line:
                        return True
                    else:
                        return False
        return True
