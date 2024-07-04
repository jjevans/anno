import sys
from anno.service import kegg

#get kegg id for a gene symbol
#jje 07032024

try:
	genesym = sys.argv[1]
except:
	message = "usage: kegg_id_by_genesym gene_symbol\n"
	sys.stderr.write(message)
	exit(1)
	
kegg_obj = kegg.API()

id = kegg_obj.id_by_genesym(genesym)

print(f"kegg id:\t{id}\tgene symbol:\t{genesym}")

exit()
