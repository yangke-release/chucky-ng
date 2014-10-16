.. Chucky documentation master file, created by
   sphinx-quickstart on Thu Oct 16 02:24:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Chucky's documentation!
==================================

This document is for `this version <http://github.com/yangke/chucky-ng/>`_ of Chucky implementation. It's modified by Ke Yang based on this `paper <http://pan.baidu.com/s/1kTwt9mJ/>`_ and `original version <https://github.com/a0x77n/chucky-ng/>`_ (developed by Alwin Maier and `Fabian Yamaguchi <http://codeexploration.blogspot.de/>`_) .
 
Introduction of Chucky
----------------------
Chucky is a the missing check vulnerability detection method designed by `Fabian Yamaguchi <http://codeexploration.blogspot.de/>`_.
It statically taints source code and identifies anomalous or missing conditions linked to security-critical objects.
Chucky analyzes functions for anomalies. To this end, the usage of symbols
used by a function is analyzed by comparing the checks used in conjunction
with the symbol with those used in similar functions.

The Implementation
------------------
This implemetation of Chucky interactive with the database parsed by `joern <http://github.com/fabsx00/joern>`_ (another tools developed by Fabian et al). 
After a Robust Parsing by joern, conditions, assignments and API symbols are extracted from every function and all the code information are stored in the graph database as Code Property Graphs including AST,CFG and DDG. Joern use Neo4j to store these information.

There are five step for Chucky to complete the analyze.

1. **Identification of sources and sinks.** The query symbol is given by user as an analyse target. So the first job of Chucky is to locate them in the database and find all the candidates(functions that use the query symbol). According to differrent symbol type, this can be achived by a group of a well defined gremlin query.
2. **Neighborhood discovery.** 

   * Viewing the function as a document and defining the key words as the element concerned in the AST, Chucky describe each function as a symbol vector. 
   * Chucky find the similarest top k functions to the query function by applying the information retrieval technique in this vector space.

   The first procedure is implemented by gremlin query in `joern-tools <http://github.com/fabsx00/joern-tools/>`_ and the secord one is implemented by pure python. 
3. **Lightweight tainting.**
   Idendify the the condition code of **if**, **while** and **for** in which there exists symbol in the path from souce to sinks. These symbols may influence or be influence by the the query symbol in each top k similarest functions. This step is also implemented by gremlin query as such relations can be descripbed as a path in the code property graph.
4. **Embedding of functions.**
   Describe each function as a sparse 0-1 vector according to the existence of the condition key word discovered by the pervious step. 
5. **Anomaly detection.**
   Find the most significant missing word in the condition vector of the query function set off by the neighborhoods. The anomaly score of the query function can then be expressed by the existing percentage in the neighborhoods.

All the analysis are based on the extensible query language defined in `joern-tools <http://github.com/fabsx00/joern-tools/>`_ by `Gremlin <https://github.com/tinkerpop/gremlin/>`_ and a wrapped inteface defined by `python-joern <http://github.com/fabsx00/python-joern/>`_.

For more about orginal idea, please refer to `Chucky: Exposing Missing Checks in Source Code for Vulnerability Discovery <http://user.informatik.uni-goettingen.de/~fyamagu/pdfs/2014-oakland.pdf/>`_ Fabian Yamaguchi, Christian Wressnegger, Hugo Gascon, and K. Rieck *ACM Conference on Computer and Communications Security (CCS)*

About the Modification.
-----------------------
1. Refactor to clean the middle code.
    * Replace sally embedding module by pure python(transplant the code witten by Fabian) to remove the data exchange cost on disk.
    * Fix some bug and make it more robust.
2. Rewirte the KNN class to support the neighborhood selection strategy:
    * Leverage name(file name or function name) information and caller set information when it's usefull.
    * Kick some name irrelevant functions out, and set a robust multiselective threshold for the recomandation of good candidate.  

Consult this `paper <http://pan.baidu.com/s/1kTwt9mJ/>`_, if you are interested in it. 
For more information or bug report please do not hesitate to contact me. Ke Yang(123yangke321@sina.com)
 
Although this is a non-official document for Chucky, hope it will be helpful for people who are intersted in Chucky and working and studying this area.  
Still trying to update the document.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   quick_start
   experiment_tutorial

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

