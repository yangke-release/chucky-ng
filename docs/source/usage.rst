Usage
=====
Example 1
---------
:: 

    $ python chucky.py -i parameter -n 25  length

Example 2
---------
::

    $ python chucky.py -i function -n 25  --interactive png_handle_sCAL

Usage Pattern
-------------
Suppose we have already parsed the code and we have configured and started the neo4j database service.
(For parsing the code and database configuration please refer to the `document <http://joern.readthedocs.org/en/latest/>`_ of `joern <https://github.com/fabsx00/joern/>`_. Don't worry, the section :ref:`quickstart` will also mention a little about this.)::

    $ cd chucky-ng/chucky
    $ python chucky.py [-h] [-i {function,callee,parameter,variable}]
                 [-n N_NEIGHBORS] [-c CHUCKY_DIR] [--interactive] [-l LIMIT]
                 [-d | -v | -q]
                 identifier

    
positional arguments::

    identifier            The name of the identifier (function name or
                        source/sink name)

optional arguments::

    -h, --help            show this help message and exit
    -i {function,callee,parameter,variable}, --identifier-type {function,callee,parameter,variable}
                        The type of identifier the positional argument
                        ``identifier`` refers to.
    -n N_NEIGHBORS, --n-neighbors N_NEIGHBORS
                        Number of neighbours to consider for neighborhood
                        discovery.
    -c CHUCKY_DIR, --chucky-dir CHUCKY_DIR
                        The directory holding chucky's data such as cached
                        symbol embeddings and possible annotations of sources
                        and sinks.
    --interactive         Enable interactive mode. Under this mode you can talk to chucky and run the analysis step by step.
    -l LIMIT, --limit LIMIT
                        Limit analysis to functions with given name
    -d, --debug           Enable debug output.
    -v, --verbose         Increase verbosity.
    -q, --quiet           Be quiet during processing.

To get a quick start, please see :ref:`quickstart`.
