# Bitstream Viewer

The purpose of this tool is to visualize the bits and their corresponding tags in a given bitstream.

# Building

make BITSTREAM=/path/to/bitstream.bit PRJXRAY=/path/to/prjxray

This will generate an html page with the data for the provided bitstream (specified by the ``BITSTREAM`` variable) using the database from the directory specified by the ``PRJXRAY`` variable.
The resulting page will be placed in the ``dist`` directory.

# Limitations

Currently the viewer is able to process 7-series bitstreams only.
