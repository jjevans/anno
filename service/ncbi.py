#ncbi eUtils query
#jje 06302024
import xml.etree.ElementTree as ET
import os
import requests as req

class API():
	#use e-utils query service
	
	def __init__(self, baseurl="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"):
		self.baseurl = baseurl
		
	def query(self, url, data=dict()):
		#make api query to url with optional dictionary data of restful parameters
		#returns xml element tree object of response text
		res = req.get(url, params=data)
		
		if res.status_code != 200:#unsuccessful
			message = f"ERROR: call to EUtils API returned response code {res.status_code}, query={url}, data={data}\n"
			raise Exception(message)

		return res.text
		
	def gene_sym_to_entrez(self, genesymbol):
		'''
		query for entrez gene id from gene symbol
		returns first result, if found, or None if not found
		queries for preferred gene symbol and may be reference to aliased symbol
		esearch.fcgi?db=<database>&term=<query>
		'''
		nonce = "esearch.fcgi"
		url = os.path.join(self.baseurl, nonce)
		
		term = f"Homo+sapiens[ORGN]+{genesymbol}[PREF]"
		data = {"db": "gene", "retmax":1000, "term": term}

		elem = ET.fromstring(self.query(url, data=data))
		
		numres = int(elem.find("Count").text)
		if numres > 0:#identifier found
			return elem.find("IdList/Id").text

		return#no result