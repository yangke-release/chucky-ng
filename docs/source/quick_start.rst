.. _quickstart:

A Quick Start Example
=====================
Suppose we are the planning to analyse the code of image processing library LibPNG(version 1.2.44).

Download and Extract
--------------------
Download and extract the the source code of libPNG.
::

    $ wget http://sourceforge.net/projects/libpng/files/libpng12/older-releases/1.2.44/libpng-1.2.44.tar.gz/download
    $ tar xvzf libpng-1.2.44.tar.gz

Generate the graph database
---------------------------
Run the following command::

    $ joern libpng-1.2.44
    
A hidden directory ``.joernIndex`` will be generated under the current directory(suppose the current directory is ``$TEST``).

Configure Database Server
-------------------------
Configure the graph database server `Neo4j <http://www.neo4j.org/>`_

Assume ``$NEO4J_HOME`` is the install directory of your Neo4j(Note that current joern only support 1.9.* version serials).
Edit the file ``$NEO4J_HOME/conf/server.properties``.
As an example, for neo4j-1.9.7, you should open the file ``neo4j-1.9.7/conf/neo4j-server.properties``.

Then change::

    #org.neo4j.server.database.location=data/graph.db

to::

    #org.neo4j.server.database.location=$TEST/.joernIndex

and save it.

Start Neo4j
-----------
Start Neo4j database.
::

    $ $NEO4J_HOME/bin/neo4j start

Go to your chucky directory ``chucky-ng/chucky`` and run a chucky analysis.
::

    $python chucky.py --parameter length -n 25 |sort -r -k 1

Then Chucky will generate the report to the screen::

    0.88000	process_data                  	    132644	Parameter	png_uint_32	length	length	0.983107493958	1.0	1.0	2	1.0	1.0	0.815409836066	libpng-1.2.44/example.c:456:0:16681:17622
    0.88000	png_write_chunk_start         	     21892	Parameter	png_uint_32	length	length	0.975450572893	0.928054375804	0.704646464646	2	1.0	1.0	0.816124031008	libpng-1.2.44/pngwutil.c:98:0:3409:4075
    0.88000	png_handle_sCAL               	      7855	Parameter	png_uint_32	length	length	0.63227508134	0.507639451767	0.172121212121	2	0.945813565657	0.828125819558	0.872698412698	libpng-1.2.44/pngrutil.c:1784:0:52039:56355
    0.88000	png_handle_pCAL               	      7142	Parameter	png_uint_32	length	length	0.617219406464	0.511462981179	0.172121212121	2	0.977463152359	0.937841008024	1.11206349206	libpng-1.2.44/pngrutil.c:1650:0:47947:51972
    0.88000	png_handle_hIST               	      6432	Parameter	png_uint_32	length	length	0.600609501799	0.522933569414	0.172121212121	2	0.975361631577	0.931775770766	0.905714285714	libpng-1.2.44/pngrutil.c:1509:0:44387:45688
    0.48000	png_push_handle_zTXt          	    130041	Parameter	png_uint_32	length	( length $CMP $NUM )	0.804980702214	0.616538090133	0.799191919192	2	0.587308060203	0.276431948855	0.444031007752	libpng-1.2.44/pngpread.c:1303:0:35814:36896
    0.48000	png_push_handle_tEXt          	    129600	Parameter	png_uint_32	length	( length $CMP $NUM )	0.707602959945	0.617204380364	0.799191919192	2	0.587308060203	0.276431948855	0.444031007752	libpng-1.2.44/pngpread.c:1205:0:33161:34165
    0.48000	png_push_handle_iTXt          	    130979	Parameter	png_uint_32	length	( length $CMP $NUM )	0.707602959945	0.609186311476	0.799191919192	2	0.587308060203	0.276431948855	0.444031007752	libpng-1.2.44/pngpread.c:1504:0:41498:42502
    0.48000	png_handle_zTXt               	      9120	Parameter	png_uint_32	length	( length $CMP $NUM )	0.534132372523	0.505309332701	0.172121212121	2	0.726729651309	0.435784343492	0.535555555556	libpng-1.2.44/pngrutil.c:2087:0:60146:63431
    0.48000	png_handle_tEXt               	      8636	Parameter	png_uint_32	length	( length $CMP $NUM )	0.550960876087	0.503936396174	0.172121212121	2	0.720901333618	0.424754228003	0.527301587302	libpng-1.2.44/pngrutil.c:1984:0:57502:60030

Following table explains some of the key column.

+---------------+-------------------+------------+--------------+--------------------------+------------------------------------------------+
| column 1      | column 2          | column 3   | column 6     |  column 7                |  column 15                                     |
+===============+===================+============+==============+==========================+================================================+
| anomaly score | function name     | node id    | query symbol | sinificant missing symbol| function location                              |
+---------------+-------------------+------------+--------------+--------------------------+------------------------------------------------+
| 0.88000       | png\_handle\_sCAL | 7855       | length       | length                   | libpng-1.2.44/pngrutil.c:1784:0:52039:56355    |
+---------------+-------------------+------------+--------------+--------------------------+------------------------------------------------+


Analysis
--------
For the vulnerable function **png\_handle\_sCAL** as reported in CVE-2011-2692, we can see from the result that it is ranked in top 5(all the top 5 functions have the highest anomaly score 0.88).
This is because most of the similar functions(the first column shows the percentage) perform the check for the parameter **length**, howerver, **png\_handle\_sCAL** doesn't check it. We call these similar functions the neighborhoods of  **png\_handle\_sCAL**.
Chucky is a efficient tool for checking such statistically significant missing case. 
