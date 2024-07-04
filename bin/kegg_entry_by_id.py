import sys
from anno.service import kegg

#get kegg entry from kegg id
#jje 07032024

try:
	keggid = sys.argv[1]
except:
	message = "usage: kegg_entry_by_id kegg_id\n"
	sys.stderr.write(message)
	exit(1)
	
kegg_obj = kegg.API()

entry = kegg_obj.entry_by_id(keggid)

print(f"{entry}")

exit()
