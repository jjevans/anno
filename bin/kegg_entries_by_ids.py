import sys
from anno.service import kegg

#get multiple kegg entry from list of kegg ids
#jje 07032024

try:
	kegglst = sys.argv[1:]
except:
	message = "usage: kegg_entry_by_id kegg_id\n"
	sys.stderr.write(message)
	exit(1)
	
kegg_obj = kegg.API()

#entries = kegg_obj.entries_by_ids_raw(kegglst)
entries = kegg_obj.entries_by_ids(kegglst)

#print id<tab>entry line for each line in result
for id in entries:
	if entries[id] is None:#no result
		print(f"{id}\tNone")
	else:#result found
		lines = entries[id].split("\n")
		for line in lines:
			print(f"{id}\t{line}")

exit()
