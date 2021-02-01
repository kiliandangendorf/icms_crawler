import scrapy
from scrapy.crawler import CrawlerProcess

import filecmp

import ICMSSpider

from ImageGenerator import ImageGenerator
import notify_with_telegram

def main():
	
	TABLE_NAME="results/table"
	last_table=TABLE_NAME+"_last.html"
	current_table=TABLE_NAME+"_current.html"
	pic_file=TABLE_NAME+'.jpg'
	
	print("Start Scrapy Spider")
	#crawling exams into tables "_last" and "_current"
	process = CrawlerProcess()
	#file and class seems to be a must have
	process.crawl(ICMSSpider.ICMSSpider, last_table, current_table)
	#the script will block here until the crawling is finished
	process.start()
		
	print("Compare Files")
	#compare files
	stillsame=filecmp.cmp(last_table,current_table)
	if stillsame:
		print("Nothing new since last time :/")
	else:
		print("Changes since last time !")
		print("Render image")
		with open(current_table, 'r') as file:
			html_string=file.read().replace('\n', '')
		#render image
		ImageGenerator().from_table_string(html_string, pic_file)
		
		print("Send message")
		#UTF8 encoded finger-emoji
		finger=u'\U0001F449'
		text="*iCMS Changes!*\n"+finger+'http://icms.hs-hannover.de/'
		notify_with_telegram.notify_with_imagepath(pic_file, text)
		print("Done")

if __name__ == "__main__":
	main()
