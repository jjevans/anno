#use the kegg api for gene and pathway queries
#jje 06302024
import datetime
import os
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

	def __init__(self, max_active=3, baseurl=""):
		self.baseurl = baseurl
		self.max_active = max_active#(max is 3 api requests/second per kegg)
		self.num_active = 0#counter of current active kegg api queries 
		self.timeout_after = 3#seconds of wait time to not exceed max allowable queries per second
		self.dothrow_timeout = True#if True raise exception if wait of max allowable queries exceeds timeout_after seconds
		self.ts = None#timestamp of last kegg api query
		
	def query(self, nonce):#change nonce to be full url with self.baseurl included?
		#execute kegg api query GET
		#nonce is the api suffix url ("operation/argument above without the kegg base url)
		#param is dictionary of data (optional)
		#NUMBER of active queries need not exceed self.max_active per second (3 per second)
		#if self.num_active = max_active queries, this method will wait on a loop until num_active is less than max_active
		#if wait exceeds self.timeout_after (seconds), then throws exception if self.dothrow_timeout is True
		sleeplen = 0.25#seconds to wait to see if less than max_active queries
		max_wait_attempt = self.timeout_after/sleeplen
		
		#wait if number of active queries is at the maximum allowable queries
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
		
		#query
		
		#make url.  do here or have as input as full url?
		url = os.path.join(self.baseurl, nonce)
		sys.stdout.write(f"request: {url}\n")
		
		res = req.get(f"{self.baseurl}/{nonce})
		
		#decrement num active
		self.num_active -= 1
		
		return res.json()
	
	def keggid_by_genesym(self, genesymbol):
		#use kegg conv
		return
	
	def keggid_by_ncbigene(self, geneid):
		#use kegg conv
		return
	
	def entry_by_id(keggid):
		#use kegg get
		return
		
	def pathway_by_gene(kegggene):
		#use kegg link to get pathway by kegg id for gene
		return
 