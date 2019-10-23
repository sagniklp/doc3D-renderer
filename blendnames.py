import os 
import sys


folder_id=sys.argv[-1]
bld_dir= './bld/{}'.format(folder_id)

with open('blendlists/blendlist{}.csv'.format(folder_id),'w') as bf:
	for f in os.listdir(bld_dir):
		bf.write(os.path.join(bld_dir,f)+',')
		bf.write('\n')

