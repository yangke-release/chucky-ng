#!/usr/bin/env python2

from job.JobGenerator import JobGenerator
from chucky_engine import ChuckyEngine

import logging
import argparse
import os, sys

DESCRIPTION = """Chucky analyzes functions for anomalies. To this end, the
usage of symbols used by a function is analyzed by comparing the checks
used in conjunction with the symbol with those used in similar functions."""
DEFAULT_N = 10 #Only useful when neigther the sim_th nor k is set.
MIN_N = 1
DEFAULT_DIR = ".chucky"

PARAMETER = 'Parameter'
VARIABLE = 'Variable'
CALLEE = 'Callee'

def n_neighbors(value):
    n = int(value)
    if n < MIN_N:
        error_message = "N_NEIGHBORS must be greater than {}".format(MIN_N)
        raise argparse.ArgumentError(error_message)
    else:
        return n
    
def similarity_threshold(value):
    th = float(value)
    if th < 0.0 or th >1.0:
        error_message = "SIMILARITY_THRESHOLD should be in the range [0,1]."
        raise argparse.ArgumentError(error_message)
    else:
        return th
    
class Chucky():

    def __init__(self):
        self._init_arg_parser()
        self.args = self.arg_parser.parse_args()
        self._config_logger()
        self._create_chucky_dir()
        self.job_generator = JobGenerator(
                    function = self.args.function,
                    callees = self.args.callees,
                    parameters = self.args.parameters,
                    variables = self.args.variables)
        self.job_generator.limit = self.args.limit
        if self.args.n_neighbors == -1 and self.args.similarity_threshold == -1.0:
                    self.logger.warning('Use neighborhood number '+DEFAULT_N+' as the default k! Similarity Threshold disabled.\n')
                    self.args.n_neighbors = DEFAULT_N
        self.engine = ChuckyEngine(
            self.args.chucky_dir,
            self.args.n_neighbors,
            self.args.similarity_threshold)

    def _init_arg_parser(self):
        self.arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
        #self.arg_parser.add_argument(
         #       'identifier',
          #      help = """The name of the identifier 
           #     (function name or source/sink name)""")
        
        
        #self.arg_parser.add_argument(
         #       '-i', '--identifier-type',
          #      action = 'store',
           #     default = 'function',
            #    choices = ['function', 'callee', 'parameter', 'variable'],
             #   help = """The type of identifier the positional argument
              #  `identifier` refers to.""")
        
        self.arg_parser.add_argument(
                '-f', '--function',
                action = 'store',
                default = None,
                help = 'Specify the function to analysis. If this option is configured, the analysis will only perform on this function.')        
        self.arg_parser.add_argument(
                '--callee',
                action='append',
                dest='callees',
                default=[],
                help='Specify the identifier name of callee type source/sink')
        
        self.arg_parser.add_argument(
                '-p','--parameter',
                action='append',
                dest='parameters',
                default=[],
                help='Specify the identifier name of parameter type source/sink')
        
        self.arg_parser.add_argument(
                '-var','--variable',
                action='append',
                dest='variables',
                default=[],
                help='Specify the identifier name of variable type source/sink')
        
        self.arg_parser.add_argument(
                '-n', '--n-neighbors',
                action = 'store',
                default = -1,
                type = n_neighbors,
                help = """Number of neighbours to consider for neighborhood
                discovery.""")
        self.arg_parser.add_argument(
                '-c', '--chucky-dir',
                action = 'store',
                default = DEFAULT_DIR,
                help = """The directory holding chucky's data such as cached
                symbol embeddings and possible annotations of sources and
                sinks.""")
        self.arg_parser.add_argument(
                '--interactive',
                action = 'store_true',
                default = False,
                help = """Enable interactive mode.""")
        self.arg_parser.add_argument(
                '-l', '--limit',
                action = 'store',
                default = None,
                type = str,
                help = """Limit analysis to functions with given name""")
        self.arg_parser.add_argument(
                '-s', '--similarity-threshold',
                action = 'store',
                default = -1.0,
                type = similarity_threshold,
                help = """Specify the minmum similarity threshold of the last neighborhood. If the top-k nearest neighborhood does not satisfy this condition then the program will stop analysis and give a WARNING:'No good enough top-k neighborhoods found!'.""")         
        group = self.arg_parser.add_mutually_exclusive_group()
        group.add_argument(
                '-d', '--debug',
                action = 'store_const',
                const = logging.DEBUG,
                dest = 'logging_level',
                default = logging.WARNING,
                help = """Enable debug output.""")
        group.add_argument(
                '-v', '--verbose',
                action = 'store_const',
                const = logging.INFO,
                dest = 'logging_level',
                default = logging.WARNING,
                help = """Increase verbosity.""")
        group.add_argument(
                '-q', '--quiet',
                action = 'store_const',
                const = logging.ERROR,
                dest = 'logging_level',
                default = logging.WARNING,
                help = """Be quiet during processing.""")

    def _create_chucky_dir(self):
        basedir = self.args.chucky_dir
        if not os.path.isdir(basedir):
            self.logger.debug('Creating directory %s.', os.path.abspath(basedir))
            os.makedirs(basedir)
        self.logger.info('Base directory is %s.', os.path.abspath(basedir))

    
    def _config_logger(self):
        self.logger = logging.getLogger('chucky')
        self.logger.setLevel('DEBUG')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.args.logging_level)
        file_handler = logging.FileHandler('chucky.log', 'w+')
        file_handler.setLevel('DEBUG')
        #console_formatter = logging.Formatter('%(message)s')
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        file_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    """
    Generates Jobs (list of ChuckyJobs) and asks
    the engine to perform an analysis for each job.
    """     
    def execute(self):
        needcache,jobsdict = self.job_generator.generate()
        jobs=[]
        for configs in jobsdict.values():
            jobs+=list(configs)
        jobs_total_num=len(jobs)        
        if needcache:
            jobsetnum=len(jobsdict)
            jobcount=0
            for j,(key,jobset) in enumerate(jobsdict.items(),1):
               if len(jobset)<self.args.n_neighbors+1 and self.args.limit==None:
                   sys.stderr.write('JobSet(%d)[source/sink:%s(%d Job)] skiped\n' %(j,str(key),len(jobset)))
                   jobcount+=len(jobset)
                   continue
               description="/%d]:JobSet(%d/%d)" %(jobs_total_num,j,jobsetnum)
               flag=self.analyzeJobSet(jobset,description,jobcount)
               if not flag:return
               jobcount+=len(jobset)
        else:
            self.analyzeJobSet(jobs,'')         
        
                    
            
    def analyzeJobSet(self,jobs,info,jobcount=None):
        numberOfJobs = len(jobs)
        
        for i, job in enumerate(jobs, 1):
            inerinfo='Job ({}/{}): {}\n'.format(
                                        i,
                                        numberOfJobs,
                                        job) 
            if info=='':
                information= inerinfo              
            else:
                information= '['+str(jobcount+i)+info+inerinfo
            sys.stderr.write(information)
            if self.args.interactive:
                choice = raw_input('Run job ([yes]/no/quit)? ').lower()
                if choice in ['n', 'no']:
                    continue
                elif choice in ['q', 'quit']:
                    return False
            self.engine.analyze(job)        
        return True

if __name__ == '__main__':
    Chucky().execute()
