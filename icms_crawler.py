import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
import filecmp
#for touch
from pathlib import Path
#for rename
import os
#for cleaning html
import w3lib.html
#import icms login data
import login_credentials

table_name="table"
overview_name="overview"

# skeleton from https://doc.scrapy.org/en/latest/topics/request-response.html
def authentication_failed(response):
	# Check the contents of the response and return True if it failed or False if it succeeded.
	# Check if new page contains loginname (binary)
	if login_credentials.loginname.encode() in response.body:
		return False
	else:
		return True

class ICMSSpider(scrapy.Spider):
	name = 'icmsspider'
	start_urls = ['http://icms.hs-hannover.de/']

	def parse(self, response):
		return scrapy.FormRequest.from_response(
			response,
			formdata={'asdf': login_credentials.loginname, 'fdsa': login_credentials.loginpw, 'submit': 'Anmelden'},
			callback=self.after_login		
		)

	def after_login(self, response):
		if authentication_failed(response):
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
					callback=self.examsMenu1
				)

	def examsMenu1(self, response):
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
				callback=self.examsMenu2
			)

	def examsMenu2(self, response):
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
				callback=self.examsOverview
			)

	def examsOverview(self, response):
		self.logger.info("found overview")
		# save overview
		self.logger.info("write overview files")
		self.swapAndSaveFiles(response,overview_name+"_last.html",overview_name+"_current.html")
		#
		#find table
		sel = Selector(response)
		table = sel.xpath("//*[@id='wrapper']/div[contains(@class,'divcontent')]/div[contains(@class,'content')]/form/table[2]").get()
		if(not table):
			self.logger.error("Can't find credits table...")
			return
		else:
			# there is still some unique links in it
			self.logger.info("remove unique links in table")
			table=self.removeLinks(table)
			# save table
			self.logger.info("write table files")
			self.swapAndSaveFiles(table,table_name+"_last.html",table_name+"_current.html")
			# compare
			stillsame=filecmp.cmp(table_name+"_last.html",table_name+"_current.html")
			if stillsame:
				self.logger.info("Nothing new since last time :/")
			else:
				self.makeCoolAndAwesomeActionOnNewResults(table, response)

	def removeLinks(self, element):
		return w3lib.html.remove_tags(element, which_ones=('a'))
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

	def makeCoolAndAwesomeActionOnNewResults(self, table, wholeresponse):
		self.logger.info("CHANGES TO LAST TIME!")
		#todo five info with table or whole overview

