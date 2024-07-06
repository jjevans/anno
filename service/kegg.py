#use the kegg api for gene and pathway queries
#jje 06302024
from anno.service import ncbi
import datetime
import os
import re
import requests as req
import sys
import time

class API():
	#base web service query
	#https://rest.kegg.jp/<operation>/<argument>[/<argument2[/<argument3>
	'''
	/get/C01290+G00092	  	retrieves a compound entry and a glycan entry
	/get/hsa:10458+ece:Z5100	  	retrieves a human gene entry and an E.coli O157 gene entry
	/get/hsa:10458+ece:Z5100/aaseq	  	retrieves amino acid sequences of a human gene and an E.coli O157 gene
	/get/C00002/image	  	retrieves the gif image file of a compound
	/get/hsa00600/image	  	retrieves the png image file of a pathway map
	/get/map00600/image2x	  	retrieves the doubled-sized png image file of a reference pathway map New!
	/get/hsa00600/conf	  	retrieves the conf file of a pathway map
	/get/hsa00600/kgml	  	retrieves the kgml file of a pathway map
	/get/br:br08301	  	retrieves the htext file of a brite hierarchy
	/get/br:br08301/json	  	retrieves the json file of a brite hierarchy
	'''
	'''
	convert id
	
	
	/conv/eco/ncbi-geneid	  	conversion from NCBI GeneID to KEGG ID for E. coli genes
	/conv/ncbi-geneid/eco	  	opposite direction
	/conv/ncbi-proteinid/hsa:10458+ece:Z5100	  	conversion from KEGG ID to NCBI ProteinID
	/conv/genes/ncbi-geneid:948364	  	conversion from NCBI GeneID to KEGG ID when the organism code is not known

	'''
	'''
	
	list all...
	
	
	/list/pathway	  	returns the list of reference pathways
	/list/pathway/hsa	  	returns the list of human pathways
	/list/organism	  	returns the list of KEGG organisms with taxonomic classification
	/list/hsa	  	returns the entire list of human genes with gene types and chromosomal positions
	/list/T01001	  	same as above
	/list/hsa:10458+ece:Z5100	  	returns the list of a human gene and an E.coli O157 gene
	/list/C01290+G00092	  	returns the list of a compound entry and a glycan entry
	'''
	'''
	LINK get entries from one database from entry a different database
	
	
	/link/pathway/hsa	  	KEGG pathways linked from each of the human genes
	/link/hsa/pathway	  	human genes linked from each of the KEGG pathways
	/link/pathway/hsa:10458+ece:Z5100	  	KEGG pathways linked from a human gene and an E. coli O157 gene
	/link/genes/K00500	  	List of genes with the KO assignment of K00500
	/link/hsa/hsa00010	  	List of human genes in pathway hsa00010
	/link/ko/map00010 or /link/ko/ko00010	  	List of KO entries in pathway map00010 or ko00010
	/link/rn/map00010 or /link/rn/rn00010	  	List of reaction entries in pathway map00010 or rn00010
	/link/ec/map00010 or /link/ec/ec00010	  	List of EC number entries in pathway map00010 or ec00010
	/link/cpd/map00010	  	List of compound entries in pathway map00010
	'''

	def __init__(self, max_active=3, baseurl="https://rest.kegg.jp/"):
		#remove trailing slash in baseurl
		self.baseurl = re.sub("/$", "", baseurl)
		self.max_active = max_active#(max is 3 api requests/second per kegg)
		self.num_active = 0#counter of current active kegg api queries 
		self.timeout_after = 3#seconds of wait time to not exceed max allowable queries per second
		self.dothrow_timeout = True#if True raise exception if wait of max allowable queries exceeds timeout_after seconds
		self.ts = None#timestamp of last kegg api query
		
		self.ncbi_obj = ncbi.API()#to convert gene symbol to entrez id

	def query(self, nonce):
		#execute kegg api query GET
		#nonce is the api suffix url ("/operation/argument above without the kegg base url)
		#param is dictionary of data (optional)
		#NUMBER of active queries need not exceed self.max_active per second (3 per second)
		#if self.num_active = max_active queries, this method will wait on a loop until num_active is less than max_active
		#if wait exceeds self.timeout_after (seconds), then throws exception if self.dothrow_timeout is True
		sleeplen = 0.25#seconds to wait to see if less than max_active queries
		max_wait_attempt = self.timeout_after/sleeplen
		
		#wait if number of active queries is at the maximum allowable queries
		#FUTURE: use self.ts to gauge if more than 3 api calls made per second, keep dict of active queries, delete out when response
		numwait = 0		
		while self.num_active >= self.max_active:#wait waitlen seconds and check again
			time.sleep(sleeplen)
			numwait += 1
			
			#if numwait more than number of allowable iterations of waiting for num_active to reduce
			if numwait > max_wait_attempt:#throw exception b/c over self.timeout_after seconds of waiting
				#provide time of last kegg query and number of seconds elapsed
				currtime = datetime.time.now()
				delta = currtime - self.ts
				elapsed = delta.total_seconds()		
				
				message = f"Max allowable queries reached for {self.timeout_after} consecutive seconds.  Exceeded timeout.  Last KEGG query logged {elapsed} seconds ago.\n"
				
				#warn or raise
				raise Exception("ERROR: " + message) if self.dothrow_timeout else sys.stderr.write("WARN: " + message)
		
		#increment num_active
		self.num_active += 1
		self.ts = datetime.datetime.now()#set timestamp of last query
		
		
		#make url
		#delete leading slashes in nonce
		nonce = re.sub("^/", "", nonce)
		url = f"{self.baseurl}/{nonce}"
		
		#query
		res = req.get(url)
		
		result = res.text.rstrip()
		
		#decrement num active
		self.num_active -= 1

		#return None if no result returned		
		if result == "":
			return

		return result
	
	def id_by_genesym(self, genesymbol):
		#input is human gene symbol
		#use anno.service.ncbi to convert gene symbol to entrez id
		# then self.id_by_entrez
		entrezid = self.ncbi_obj.gene_sym_to_entrez(genesymbol)
		
		if entrezid is None:#no entrez id for this gene symbol
			message = f"ERROR: No entrez id found for gene symbol: {genesymbol}"
			raise Exception(message)

		return self.id_by_entrez(entrezid)
	
	def id_by_entrez(self, entrezid):
		#input is entrez gene id and KEGG organism (hsa=human)
		#returns kegg id or None if no result
		#uses kegg conv
		#	/conv/eco/ncbi-geneid	  	conversion from NCBI GeneID to KEGG ID for E. coli genes
		#	/conv/genes/ncbi-geneid:948364	  	conversion from NCBI GeneID to KEGG ID when the organism code is not known
		nonce = f"/conv/genes/ncbi-geneid:{entrezid}"

		result = self.query(nonce)
		
		if result is None:#return None if no result returned
			return
		
		return result.split("\t")[1]#result is tab delimited string with id in 2nd col
	
	def entry_by_id(self, keggid):
		#input single string kegg identifier
		#returns entire record for that kegg entity
		#use kegg get to get kegg entries
		#/get/hsa:10458
		nonce = f"/get/{keggid}"

		result = self.query(nonce)
		
		if result is not None:#strip /// trailing delimiter
			result = re.sub("\n///$", "", result)

		return result

	def entries_by_ids_raw(self, keggids):
		#input is array of kegg ids
		#returns exact raw kegg response of all entries delimited by "///"
		#use entries_by_id to get dictionary of results
		#/get/hsa:10458+ece:Z5100

		ids = "+".join(keggids)
		nonce = f"/get/{ids}"

		return self.query(nonce)

	def entries_by_ids(self, keggids):
		#input is array of kegg ids
		#duplicate ids are ignored and not returned in duplicate
		#returns dict of key kegg id and entry as value for each inputted id_by_entrez
		rawentries = self.entries_by_ids_raw(keggids)
		
		entries = dict()
				
		if rawentries is not None:#results found	
			resarr = rawentries.split("///")

			#remove last empty entry (ends in /// so adds in extra empty element)
			resarr.pop()
		
			for result in resarr:				
				entryid = None
				organism = None			
				recordid = None
			
				lines = result.strip().split("\n")

				for line in lines:
					items = line.split()
				
					#get entry id and organism to match input ids. 
					# id may have prepended organism (hsa:3223) or just id (3223)
					if line.startswith("ENTRY"):
						entryid = items[1]

					if line.startswith("ORGANISM"):
						organism = items[1]

					if entryid is not None and organism is not None:#found id, organism
						break
				
				#error if result has organism or id not found
				if entryid is None or organism is None:#not found id, organism
					message = f"ERROR: kegg result id or organism not found.  organism={organism}, id={entryid}\n"
					raise Exception(message)

				#match to input id. check to see if organism defined in input id
				#organism:id
				recordid = f"{organism}:{entryid}"
				
				#error if record id (organism:entryid or entryid itself not in inputted ids
				if recordid not in keggids and entryid not in keggids:
					message = f"ERROR: response id not found in inputted id list: {recordid} or {entryid} not found\n"
					raise Exception(message)

				#find match		
				if keggids.index(recordid) is not None:#has organism:id
					entries[recordid] = result.strip()
				elif keggids.index(entryid) is not None:#has just id without organism
					entries[entryid] = result.strip()
		
		#ensure all input ids exist in entries dict or add id with value None
		resids = entries.keys()
		inputids = set(keggids)
		missingids = inputids - resids

		for missingid in missingids:
			entries[missingid] = None
		 
		return entries

	def pathway_by_id(self, keggpathway):
		#use kegg link to get pathway by kegg id for a kegg pathway id
		return

	def pathway_by_genes(self, kegggenes):
		#use kegg link to get pathway by list of kegg id for genes
		return

	def genes_by_pathway(self, keggpathway):
		#get genes associated to kegg pathway
		#	/link/hsa/hsa00010	  	List of human genes in pathway hsa00010
		nonce = f"/link/hsa/{keggpathway}"