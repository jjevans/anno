import sys
from anno.service import ncbi
import json

#ncbi eutils EInfo to describe database (1st argument).  List all databases with no arguments.
# reports fields to query and links available to other databases when db nane provided
#jje 06302024

try:
	dbname = sys.argv[1]
except:
	results = ncbi.API().describe_service()
	
	for entry in sorted(results["einforesult"]["dblist"]):
		print(f"DBLIST:\t{entry}")
	
	message = "\nINFO FOR SPECIFIC DATABASE FIELDS, specify a database name...\nINFO:\t\tusage: ncbi_einfo_describe.py database_name\n"
	sys.stderr.write(message)
	exit(1)
	
ncbi_obj = ncbi.API()

results = ncbi_obj.describe_service(db=dbname)

#print(json.dumps(results, indent=4))

dbinfos = results["einforesult"]["dbinfo"]
for dbinfo in dbinfos:
	
	db = dbinfo["dbname"]
	fields = dbinfo["fieldlist"]
	links = dbinfo["linklist"]

	#print available fields to query from
	for resdict in fields:
		print(f"FIELD:\tdb={db}\tname={resdict['name']}\tfullname={resdict['fullname']}\tsingletoken={resdict['singletoken']}\tdescription={resdict['description']}")

	#print db links
	for resdict in links:
		print(f"LINK:\tdb={db}\tname={resdict['name']}\tdbto={resdict['dbto']}\tfullname={resdict['menu']}\tdescription={resdict['description']}")
	
exit()
