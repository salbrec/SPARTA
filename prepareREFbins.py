import pandas as pd
import numpy as np
from sys import argv, path, stdout
import os
import pickle
import argparse
from sklearn.ensemble import RandomForestClassifier

import utils.pp as pp
import utils.utils as utils

script_dir = './'
if argv[0].find('/') >= 0:
	script_dir = argv[0][: - argv[0][::-1].find('/')]

parser = argparse.ArgumentParser(description='''Given the genome assembly name, the targets of interest and the resolution (binsize),
                                                this script creates the bin files needed by SIMPA or InterSIMPA''')
parser.add_argument('--genome', '-g', type=str, default='hg38', choices=['mm10', 'hg38'], help='Genome assembly')
parser.add_argument('--targets', '-t', type=str, required=True, help='''Target(s) defining the specific reference experiments
					(ususally the one used in the scChIP). When multiple targets are provided, separate by "+"''')
parser.add_argument('--binsize', '-bs', type=str, default='5kb', help='Size of the bins (genomic regions). For instance 500bp, 1kb, 2kb, ...')

# parse and pre-process command line arguments
args = parser.parse_args()
bin_size_int = int(args.binsize.replace('bp', '').replace('kb', '000'))
ENCODE_dir = '%sdata/ENCODE/%s/%s/'%(script_dir, args.genome, args.binsize)
target_set = set(args.targets.split('+'))

# get reference experiments for given target(s)
metadata = pd.read_csv('%sdata/metadata_ENCODE.tsv'%(script_dir), sep='\t')
metadata = metadata.loc[metadata['assembly'] == args.genome]
metadata = metadata.loc[[True if target in target_set else False for target in metadata['target']]]
print('Number of available bulk reference experiments: %d (for %s)'%(metadata.shape[0],args.targets))

allowed_chroms = utils.get_allowed_chrom_str(args.genome)
chrom_sizes = utils.get_chrom_sizes('%sdata/chromosome_sizes/%s/sizes.tsv'%(script_dir, args.genome))

bins_dir = './data/ENCODE/%s/%s/'%(args.genome, args.binsize)
if not os.path.exists(bins_dir):
    os.mkdir(bins_dir)

for index, row in metadata.iterrows():
	acc = row['accession']
	bins_file = '%s%s'%(bins_dir, acc)
	if os.path.exists(bins_file):
		print('The bins for %s already exist.'%(acc))
		continue

	bed_file = './data/ENCODE/%s/bed/%s.bed'%(args.genome, acc)
	peaks = pp.get_peaks(bed_file, allowed_chroms, enrich_index=-1)
	sc_bins, sc_bin_value, max_bin_ID, bin_bed_map = pp.bin_it(peaks, allowed_chroms,
					chrom_sizes, bin_size_int)
	print(index, acc, type(sc_bins), len(sc_bins))
	pickle.dump(sc_bins, open(bins_file, 'wb'))




'''

allowed_chroms = utils.get_allowed_chrom_str()
chrom_sizes = utils.get_chrom_sizes('%sdata/chromosome_sizes/%s/sizes.tsv'%(script_dir, args.genome))
peaks = pp.get_peaks(args.bed, allowed_chroms, enrich_index=-1)
sc_bins, sc_bin_value, max_bin_ID, bin_bed_map = pp.bin_it(peaks, allowed_chroms,
                                                        chrom_sizes, bin_size_int)
sc_bins = sorted(list(sc_bins))
print('\nGiven the sparse input there are %d genomic regions converted into %d bins of size %s'%(
    sum([len(p) for p in peaks.values()]), len(sc_bins), args.binsize))






given:
    assembly target binsize (1kb)

 create dir for bin size

 i also need the chromosome sizes...

 go for it...

'''
