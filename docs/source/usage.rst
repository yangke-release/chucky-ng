Usage
=====
Example 1
---------
:: 

    $ python chucky.py --p length -n 25 --interactive

Example 2
---------
::

    $ python chucky.py -p length --callee png_free -var slength -n 3 -l png_handle_sCAL -r

Usage Pattern
-------------
Suppose we have already parsed the code and we have configured and started the neo4j database service.
(For parsing the code and database configuration please refer to the `document <http://joern.readthedocs.org/en/latest/>`_ of `joern <https://github.com/fabsx00/joern/>`_. Don't worry, the section :ref:`quickstart` will also mention a little about this.)::

    $ cd chucky-ng/chucky
    $ python chucky.py [-h] [-f FUNCTION] [--callee CALLEES [CALLEES ...]]
                 [-p PARAMETERS [PARAMETERS ...]]
                 [-var VARIABLES [VARIABLES ...]] -n N_NEIGHBORS
                 [-c CHUCKY_DIR] [-o OUTPUT_REPORT_DIRECTORY] [-r]
                 [--interactive] [-l LIMIT] [-d | -v | -q]

optional arguments::

    -h, --help          Show this help message and exit.
    -f FUNCTION, --function FUNCTION
                        Specify the function to analysis. 
			If this option is configured, the analysis will only perform on this function.
    -n N_NEIGHBORS, --n-neighbors N_NEIGHBORS
                        Number of neighbours to consider for neighborhood discovery.
    -c CHUCKY_DIR, --chucky-dir CHUCKY_DIR
                        The directory holding chucky's data such as cached
                        symbol embeddings and possible annotations of sources and sinks.
    -o OUTPUT_REPORT_DIRECTORY, --output-report-directory OUTPUT_REPORT_DIRECTORY
                        The report output directory of chucky. For each target function under
                        analyzation chucky will generate a detail report.
    -r, --report        Output the detail report for each function under analyzation.
    --interactive       Enable interactive mode.
    -l LIMIT, --limit LIMIT
                        Limit analysis to functions with given name.
    -d, --debug         Enable debug output.
    -v, --verbose       Increase verbosity.
    -q, --quiet         Be quiet during processing.
    
source_sinks::

    --callee CALLEES [CALLEES ...]
                        Specify the identifier name of callee type source/sink.
    -p PARAMETERS [PARAMETERS ...], --parameter PARAMETERS [PARAMETERS ...]
                        Specify the identifier name of parameter type source/sink.
    -var VARIABLES [VARIABLES ...], --variable VARIABLES [VARIABLES ...]
                        Specify the identifier name of variable type source/sink.

To get a quick start, please see :ref:`quickstart`.
