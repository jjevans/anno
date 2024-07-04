import sys
from anno.service import kegg

#get kegg id from entrez gene id
#jje 07032024

try:
	entrezid = sys.argv[1]
except:
	message = "usage: kegg_id_by_entrez.py entrez_id\n"
	sys.stderr.write(message)
	exit(1)
	
kegg_obj = kegg.API()

id = kegg_obj.id_by_entrez(entrezid)

print(f"kegg id:\t{id}\tentrez id:\t{entrezid}")

exit()
