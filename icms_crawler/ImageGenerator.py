import imgkit

class ImageGenerator():
	def __init__(self):
		self.options={
			'format': 'jpg', #jpeg huge smaller than png
			'encoding': "UTF-8"
		}
		self.css='css/QISDesign_HSH_wihtout_inputs.css'
	
	def from_file(self, filename, outfile):
		imgkit.from_file(filename, outfile, options=self.options, css=self.css)
	
	def from_table_string(self, html_string, outfile):
		html_string=self.surround_by_html_tags(html_string)
		imgkit.from_string(html_string, outfile, options=self.options, css=self.css)
	
	def surround_by_html_tags(self, html_string):
		prefix='<html><head><meta charset="UTF-8" /></head><body>'
		postfix='</body></html>'
		return prefix+html_string+postfix

