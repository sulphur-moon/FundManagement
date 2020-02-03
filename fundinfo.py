import requests
import execjs


class FundInfo:
	def __init__(self, url='http://fund.eastmoney.com/js/fundcode_search.js'): 
		js = requests.get(url)
		docjs = execjs.compile(js.text)
		self.fundlist = docjs.eval('r')
		return
	
	def get_list(self):
		return self.fundlist
	
	def get_fundinfo(self, code):
		url = 'http://fund.eastmoney.com/pingzhongdata/' + code + '.js'
		js = requests.get(url)
		docjs = execjs.compile(js.text)
		return docjs
