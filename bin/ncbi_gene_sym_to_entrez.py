import sys
from anno.service import ncbi

#convert gene symbol to entrez id with ncbi eutils
#attempts to find single entrez id for symbol
#if no exact match (ambigous), attempts to find all ids for that symbol
#jje 06302024

try:
	genesym = sys.argv[1]
except:
	message = "usage: ncbi_gene_sym_to_entrez.py gene_symbol\n"
	sys.stderr.write(message)
	exit(1)
	
ncbi_obj = ncbi.API()

#try to find unambigous preferred id 
ids = ncbi_obj.gene_sym_to_entrez(genesym, onlypreferred=True)

if ids is not None:#found preferred
	print(f"entrez id (preferred):\t{ids[0]}\tgene symbol:\t{genesym}")
else:
	ids = ncbi_obj.gene_sym_to_entrez(genesym, onlypreferred=False)
	
	if ids is not None:#found ids for ambiguous results
		for id in ids:
			print(f"entrez id (ambiguous):\t{id}\tgene symbol:\t{genesym}")

exit()
