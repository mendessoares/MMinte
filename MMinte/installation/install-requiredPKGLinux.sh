#! /bin/bash

# Select version of BLAST.
VERSION=2.2.22

# Download BLAST 2.2.22 package from NCBI FTP site.
ftp ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/${VERSION}/ncbi-blast-${VERSION}+-x64-linux.tar.gz

# Unzip the package.
tar xfz ncbi-blast-${VERSION}+-x64-linux.tar.gz

# Create a .ncbirc file with the location of the data subdirectory.
#cat <<-EOF >blast-${VERSION}/.ncbirc
#	[NCBI]
#	Data=blast-${VERSION}/data
#EOF

# Cleanup.
rm ncbi-blast-${VERSION}+-x64-linux.tar.gz

pip install numpy
pip install -r requirements.txt


exit 0
