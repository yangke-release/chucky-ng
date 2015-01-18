chucky-ng
==============

Introduction
--
This program implements the missing check detection method named "Chucky".
Chucky statically taints source code and identifies anomalous or missing conditions linked to security-critical objects.
Chucky analyzes functions for anomalies. To this end, the usage of symbols
used by a function is analyzed by comparing the checks used in conjunction
with the symbol with those used in similar functions. Consult [here](http://chucky.readthedocs.org/) for more detail document.

Dependencies
--
+ joern >= 2.0 <https://github.com/fabsx00/joern>
+ joern-tools >=0.1 <https://github.com/fabsx00/joern-tools>
+ Neo4j 1.9 <http://www.neo4j.org>
+ Python 2.7

This version is for Debian & Ubuntu Linux only.

Fetch and Installation
--
Run the following command in the terminal:
From GIT repository first run

    $ sudo apt-get install git #skip this command if you have git already installed
    $ git clone https://github.com/yangke/chucky-ng.git
    
Usage
--
Suppose we have already parse the code and we have configured and started the neo4j database service.
(For parsing the code and database configuration please refer to the [document](http://joern.readthedocs.org/en/latest/) of [joern](https://github.com/fabsx00/joern). Don't worry, the Following quick start example will also mention a little about this.)

    $ cd chucky-ng/chucky
    $ python chucky.py [-h] [-f FUNCTION] [--callee CALLEES [CALLEES ...]]
                 [-p PARAMETERS [PARAMETERS ...]]
                 [-var VARIABLES [VARIABLES ...]] -n N_NEIGHBORS
                 [-c CHUCKY_DIR] [--interactive] [-l LIMIT] [-d | -v | -q]
Example 1: 

    $ python chucky.py --parameter length -n 25 --interactive 
    
Example 2: 

    $ python chucky.py --p length --callee png_free --var slength -n 3 -l png_handle_sCAL
    
positional arguments:

    identifier          The name of the identifier (function name or
                        source/sink name)

optional arguments:

    -h, --help          show this help message and exit
    -f FUNCTION, --function FUNCTION
                        Specify the function to analysis. If this option is
                        configured, the analysis will only perform on this
                        function.
    -n N_NEIGHBORS, --n-neighbors N_NEIGHBORS
                        Number of neighbours to consider for neighborhood
                        discovery.
    -c CHUCKY_DIR, --chucky-dir CHUCKY_DIR
                        The directory holding chucky's data such as cached
                        symbol embeddings and possible annotations of sources
                        and sinks.
    --interactive         Enable interactive mode.
    -l LIMIT, --limit LIMIT
                        Limit analysis to functions with given name
    -d, --debug         Enable debug output.
    -v, --verbose       Increase verbosity.
    -q, --quiet         Be quiet during processing.
    
source_sinks:

    --callee CALLEES [CALLEES ...]
                        Specify the identifier name of callee type source/sink
    -p PARAMETERS [PARAMETERS ...], --parameter PARAMETERS [PARAMETERS ...]
                        Specify the identifier name of parameter type
                        source/sink
    -var VARIABLES [VARIABLES ...], --variable VARIABLES [VARIABLES ...]
                        Specify the identifier name of variable type
                        source/sink
    
    
A Quick Start Example.
--
Suppose we are the planning to analyse the code of image processing library LibPNG(version 1.2.44).
Download and extract the the source code of libPNG.

    $ wget http://sourceforge.net/projects/libpng/files/libpng12/older-releases/1.2.44/libpng-1.2.44.tar.gz/download
    $ tar xvzf libpng-1.2.44.tar.gz
Generate the graph database.

    $ joern libpng-1.2.44
    
A hidden directory .joernIndex will be generated under the current directory(suppose it is $TEST).

Configure the graph database server [Neo4j](http://www.neo4j.org/).

Assume $NEO4J_HOME is the install directory of your Neo4j(Note that current joern only support 1.9.* version serials).
Edit the file $NEO4J_HOME/conf/server.properties.
Take neo4j-1.9.7 as an example, you should open the file neo4j-1.9.7/conf/neo4j-server.properties.
Then change 

    #org.neo4j.server.database.location=data/graph.db
to 

    #org.neo4j.server.database.location=$TEST/.joernIndex
and save it.
Start Neo4j database. 

    $ $NEO4J_HOME/bin/neo4j start
Go to your chucky directory(chucky-ng/chucky) and run a chucky analysis.

    $python chucky.py --parameter length -n 25 |sort -r -k1

Then Chucky will generate the report to the screen.

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

| column 1      | column 2		| column 3 | column 6    |  column 7                 |  column 15                                 |
| ------------- |:---------------------:|:--------:|:-----------:|:-------------------------:|-------------------------------------------:|
| anomaly score | function name         | node id  |query symbol | sinificant missing symbol | function location                          |
| 0.88000       | png\_handle\_sCAL     | 7855     |length       | length                    | libpng-1.2.44/pngrutil.c:1784:0:52039:56355|

For the vulnerable function **png\_handle\_sCAL** as reported in CVE-2011-2692, we can see from the result that it is ranked in top 5(all the top 5 functions have the highest anomaly score 0.88).
This is because most of the similar functions(the first column shows the percentage) perform the check for the parameter **length**, howerver, **png\_handle\_sCAL** doesn't check it. We call these functions neighborhoods of  **png\_handle\_sCAL**.
Chucky is a efficient tool for checking such statistically significant missing case. 

For the orginal idea, you can refer to [Chucky: Exposing Missing Checks in Source Code for Vulnerability Discovery](http://user.informatik.uni-goettingen.de/~fyamagu/pdfs/2014-oakland.pdf)
 Fabian Yamaguchi, Christian Wressnegger, Hugo Gascon, and K. Rieck
*ACM Conference on Computer and Communications Security (CCS)*

This modified version of Chucky is based on the [original version](https://github.com/a0x77n/chucky-ng) written by Alwin Maier and [Fabian Yamaguchi](http://codeexploration.blogspot.de/).

About the Modification.
--
1. Refactor to clean the middle code.
    * Replace sally embedding module by pure python(transplant the code witten by Fabian) to remove the data exchange cost on disk.
    * Fix some bug and make it more robust.
2. Rewirte the KNN class to support the neighborhood selection strategy:
    * Leverage name(file name or function name) information and caller set information when it's usefull.
    * Kick some name irrelevant functions out, and set a robust multiselective threshold for the recomandation of good candidate.
3. Add multi-source/sink support.
    * Design a new option set for user to specify the multi-source/sink.
    * Use the combination of source/sink as the key feature to find candidate neighborhood.
    * Use the union of the tainted condition features as the condition embedding feature.
    * Refactor the job generation.

For more information or bug report please do not hesitate to contact me. Ke Yang(123yangke321@sina.com) 
 
Still trying to update the wiki document.
