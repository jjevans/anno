import sys
from anno.service import ncbi

#convert gene symbol to entrez id with ncbi eutils
#jje 06302024

try:
	genesym = sys.argv[1]
except:
	message = "usage: ncbi_gene_sym_to_entrez.py gene_symbol\n"
	sys.stderr.write(message)
	exit(1)
	
ncbi_obj = ncbi.API()

id = ncbi_obj.gene_sym_to_entrez(genesym)

print(f"entrez id:\t{id}\tgene symbol:\t{genesym}")

exit()
