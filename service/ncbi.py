#ncbi eUtils query
#jje 06302024
import json
import xml.etree.ElementTree as ET
import os
import requests as req

class API():
	#use e-utils query service
	
	def __init__(self, baseurl="https://eutils.ncbi.nlm.nih.gov/entrez/eutils", responsetype="xml"):
		self.baseurl = baseurl
		self.responsetype = responsetype

	def query(self, url, data=dict()):
		#make api query to url with optional dictionary data of restful parameters
		#returns xml element tree object of response text

		if "retmode" not in data:#make default response self.format (xml by default)
			data["retmode"] = self.responsetype
		
		res = req.get(url, params=data)

		if res.status_code != 200:#unsuccessful
			message = f"ERROR: call to EUtils API returned response code {res.status_code}, query={url}, data={data}\n"
			raise Exception(message)

		if data["retmode"] == "json":
			return res.json()

		return res.text
		
	def gene_sym_to_entrez(self, genesymbol, onlypreferred=True):
		'''
		query for entrez gene id from gene symbol in human
		onlypreferred=True will only find a single preferred entrez id for symbol (unambigous).
		onlypreferred=False will allow any gene id related to gene symbol for ambigous results
		returns list of entrez ids, if found, or None if not found
		queries for preferred gene symbol and may be reference to aliased symbol
		esearch.fcgi?db=<database>&term=<query>
		'''
		url = f"{self.baseurl}/esearch.fcgi"
		
		if onlypreferred is True:#only return if unambigous, preffered id is found
			term = f"Homo+sapiens[ORGN]+{genesymbol}[PREF]"
		else:#query for all ids mapping to this symbol (sometimes symbol is ambiguous
			term = f"Homo+sapiens[ORGN]+{genesymbol}[GENE]"
		
		data = {"db": "gene", "retmax":1000, "term": term}
		elem = ET.fromstring(self.query(url, data=data))

		numres = int(elem.find("Count").text)
		if numres == 0:#no result
			return
		
		ids = list()
		for id in elem.iterfind("IdList/Id"):
			ids.append(id.text)

		return ids
	
	def entrez_entry_by_id(self, entrezid):
		#fetch record for entrez id
		url = f"{self.baseurl}/efetch.fcgi"
		
		data = {"db": "gene", "id": str(entrezid)}

		results = self.query(url, data=data)
		print(results)

		return

	def describe_service(self, db=None):
		#describe all available db (db arg None) or specific database (db=value) using EInfo service
		url = f"{self.baseurl}/einfo.fcgi"
		
		data = {"db": db} if db is not None else dict()
		data["retmode"] = "json"
		
		return self.query(url, data=data)
