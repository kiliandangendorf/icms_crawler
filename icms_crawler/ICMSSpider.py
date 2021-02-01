import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
#for touch
from pathlib import Path
#for rename
import os
#for cleaning html
import w3lib.html

#import icms login data
import login_credentials

# skeleton from https://doc.scrapy.org/en/latest/topics/request-response.html

class ICMSSpider(scrapy.Spider):
	name = 'icmsspider'
	start_urls = ['http://icms.hs-hannover.de/']

	def __init__(self, oldfile, newfile):
		self.oldfile=oldfile
		self.newfile=newfile
	
	def parse(self, response):
		return scrapy.FormRequest.from_response(
			response,
			formdata={'asdf': login_credentials.LOGIN_NAME, 'fdsa': login_credentials.LOGIN_PW, 'submit': 'Anmelden'},
			callback=self.navigate_to_exams_menu		
		)

	def authentication_failed(self, response):
		# Check the contents of the response and return True if it failed or False if it succeeded.
		# Check if new page contains loginname (binary)
		if login_credentials.LOGIN_NAME.encode() in response.body:
			return False
		else:
			return True

	def navigate_to_exams_menu(self, response):
		if self.authentication_failed(response):
			self.logger.error("Login failed... Wrong PW?")
			return
		else:			
			self.logger.info("Login worked, nice!")
			sel = Selector(response)
			# <a href="https://icms.hs-hannover.de/qisserver/rds?state=change&amp;type=1&amp;moduleParameter=studyPOSMenu&amp;nextdir=change&amp;next=menu.vm&amp;subdir=applications&amp;xml=menu&amp;purge=y&amp;navigationPosition=functions%2CstudyPOSMenu&amp;breadcrumb=studyPOSMenu&amp;topitem=functions&amp;subitem=studyPOSMenu" class="visited " target="_self">Prüfungen</a>
			results = sel.xpath("//*[contains(@href, 'moduleParameter=studyPOSMenu')]")
			if(not results):
				self.logger.error("Can't find link to exams...")
				return
			else:
				nexturl=results[0].attrib['href']
				self.logger.info("found link: "+nexturl)
				yield Request(
					url=nexturl,
					callback=self.navigate_to_score_view
				)

	def navigate_to_score_view(self, response):
		sel = Selector(response)
		# <a href="https://icms.hs-hannover.de/qisserver/rds?state=notenspiegelStudent&amp;next=tree.vm&amp;nextdir=qispos/notenspiegel/student&amp;menuid=notenspiegelStudent&amp;breadcrumb=notenspiegel&amp;breadCrumbSource=menu&amp;asi=JJ2xAKmILbgrerCT19KM" title="" class="auflistung">Notenspiegel</a>
		results = sel.xpath("//*[contains(@href, 'qispos/notenspiegel/student&menuid=notenspiegelStudent')]")
		if(not results):
			self.logger.error("Can't find link to credits...")
			return
		else:
			nexturl=results[0].attrib['href']
			self.logger.info("found link: "+nexturl)
			yield Request(
				url=nexturl,
				callback=self.click_on_info_link
			)

	def click_on_info_link(self, response):
		sel = Selector(response)
		#https://icms.hs-hannover.de/qisserver/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabschl%3D90%2Cstgnr%3D1&expand=0&asi=JJ2xAKmILbgrerCT19KM#auswahlBaum%7Cabschluss%3Aabschl%3D90%2Cstgnr%3D1
		results = sel.xpath("//*[contains(@href, 'qispos/notenspiegel/student&createInfos=Y')]")
		if(not results):
			self.logger.error("Can't find link to credits-overview...")
			return
		else:
			nexturl=results[0].attrib['href']
			self.logger.info("found link: "+nexturl)
			yield Request(
				url=nexturl,
				callback=self.isolate_table
			)

	def isolate_table(self, response):
		self.logger.info("found exams overview")
		#find table
		sel = Selector(response)
		table = sel.xpath("//*[@id='wrapper']/div[contains(@class,'divcontent')]/div[contains(@class,'content')]/form/table[2]").get()
		if(not table):
			self.logger.error("Can't find credits table...")
			return
		else:
			# there is still some unique links in it
			# and remove not loaded images
			self.logger.info("remove unique links and unwanted tags in table")
			table=self.removeUnwandtedTags(table)
			# save table
			self.logger.info("write table files")
			#self.swapAndSaveFiles(table,self.TABLE_NAME+"_last.html",self.TABLE_NAME+"_current.html")
			self.swapAndSaveFiles(table, self.oldfile, self.newfile)

	def removeUnwandtedTags(self, element):
		return w3lib.html.remove_tags(element, which_ones=('a','img'))
		#https://w3lib.readthedocs.io/en/latest/w3lib.html

	def swapAndSaveFiles(self, response, oldfile, newfile):
		Path(oldfile).touch()
		Path(newfile).touch()
		#swaping files
		os.rename(newfile, oldfile+".tmp")
		os.rename(oldfile, newfile)
		os.rename(oldfile+".tmp", oldfile)
		#save to newfile
		f = open(newfile, "w")
		if isinstance(response, str):
			f.write(response)
		else:
			f.write(response.text)
		#f.write(response.body.decode('utf-8'))
		f.close()


