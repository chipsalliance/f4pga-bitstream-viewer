================
Bitstream Viewer
================

The purpose of this tool is to visualize the bits and their corresponding tags in a given bitstream.

This tool has two primary functions:

1. Tile View: A grid of tiles will be generated to display the features in a bitstream. Each tile that is inhabited by features will be highlighted. By clicking on a highlighted tile, a pop-up will appear with the features within that tile and their corresponding bits. This is accomplished with `Vue.js, <https://vuejs.org/>`_ a JavaScript framework. 

2. Frame View (Optional function): A grid of frames will be generated to display features in a bitstream. Each frame that contains bits associated with a feature used by the bitstream will be highlighted. By clicking on a highlighted frame, the page will be redirected to a grid of all the bits for that specific frame.  

Building
--------
::

    make BITSTREAM=/path/to/bitstream.bit PART=part_name PRJXRAY=/path/to/prjxray

This will generate an html page for the "Tile View" located in the ``dist`` directory.

Limitations
-----------

Currently the viewer is able to process 7-series bitstreams only.
