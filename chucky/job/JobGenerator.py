from job.Job import ChuckyJob
from joernInterface.indexLookup.FunctionLookup import FunctionLookup
from joernInterface.indexLookup.IdentifierLookup import IdentifierLookup
from joernInterface.indexLookup.CalleeLookup import CalleeLookup
import re

from job.Symbol import Symbol

PARAMETER = 'Parameter'
VARIABLE = 'Variable'
CALLEE = 'Callee'

"""
Creates a list of jobs for Chucky Engine based
on user queries.
"""

class JobGenerator(object):

    def __init__(self,function,callees,parameters,variables):
        self.function_name = function
        self.callee_names = callees
        self.parameter_names = parameters        
        self.variable_names = variables
        self.limit = None

    """
    Generates a joblist for the appointed function.
    @returns a list of jobs with single source/sinks).
    """
    def genJobsForFunc(self,identifier):
        configurations = []
        functions = FunctionLookup.lookup_functions_by_name(identifier)
        for function in functions:
            parameters = function.parameters()
            configurations+=self._jobs_from_symbols(parameters,function,PARAMETER)
            variables = function.variables()
            configurations+=self._jobs_from_symbols(variables,function,VARIABLE)
            callees = function.callees()
            configurations+=self._jobs_from_symbols(callees,function,CALLEE)
                
        return configurations
    
    def _jobs_from_symbols(self, symbols,function,symbol_type):
        def f(x):
            job=ChuckyJob(function)
            decl_type=function.name if symbol_type==CALLEE else x.declaration_type()
            job.addSourceSinkByString(x.code, decl_type,symbol_type) 
            return job
        return map(f, symbols)    
    
    def getIdentiferInstances(self,name,identifier_type):
        if identifier_type==CALLEE:
            db_callees=CalleeLookup.calleesByName(name)
            return db_callees
        elif identifier_type==PARAMETER:
            db_parameters = IdentifierLookup.lookup_parameter(name)
            return db_parameters
        elif identifier_type==VARIABLE:
            db_variables = IdentifierLookup.lookup_variable(name)
            return db_variables
    '''    
    Remove the invalid key(func) if its value(job) is None.
    This is a Defensive Operation. 
    '''
    def test_and_sanitize_map_have_values(self,func_job_map):
        for func,job in func_job_map.items():
            if job:
                return True;
            else:#This case may not likely to happen.
                del func_job_map[func]
        return False
    
    '''
    Generate a map from function to job in which the function is the Symbol User and the job is the unsplited mixjob.
    That means identifiers with the same name and the same SOURCE/SINK_TYPE and different declaration type may be add in the sourcesink set of the job together.
    And we can later use the split() method provide by Job Class to split to unique concrete runable job.
    
    A meta-identifier is the abstract type with three key property:
    SOURCE_SINK_TYPE, DECLAEATION_TYPE, SOURCE_SINK_NAME.
    For a concrete runable job, two source/sink with same SOURCE_SINK_NAME and SOURCE_SINK_TYPE but different DECLAEATION_TYPE should not exist.
    That means in a job for specific SOURCE_SINK_TYPE and SOURCE_SINK_NAME there should be only one meta-identifier. 
    
    @Parameter
    [list()]source/sink names,
    [list()]source/sink type(CALLEE,PARAMETER,VARIABLE),
    [dict()]func_job_map:Function->Job
    
    @return the updated [dict()]func_job_map  
    '''
    def getFuncJobMapBySourceSinkNames(self,identifierNames,identifier_type,func_job_map):
        #This function will process same type identifier.
        
        #@Defensive Operation
        have_source_sinks=self.test_and_sanitize_map_have_values(func_job_map)
        
        for identifier_name in identifierNames:
            #different name identifier
            db_identifiers = self.getIdentiferInstances(identifier_name,identifier_type)
            if len(db_identifiers)==0:return dict()
            if not have_source_sinks:#add all
                for db_identifier in db_identifiers:#same name identifier
                    job=ChuckyJob(db_identifier.function(),True)
                    job.addSourceSinkByDBIdentifier(db_identifier,identifier_type)
                    func_job_map[db_identifier.function()]=job
                have_source_sinks=True
            else:
                tmp_map=dict()
                for db_identifier in db_identifiers:
                    #same name identifier 
                    if db_identifier.function() in func_job_map.keys():
                        #just keep the function that include all of the specified identifier.
                        job=func_job_map[db_identifier.function()]
                        job.addSourceSinkByDBIdentifier(db_identifier,identifier_type)
                        tmp_map[db_identifier.function()]=job
                if len(tmp_map)==0:return dict()
                else:func_job_map=tmp_map
                
        return func_job_map 
    """
    Generates a suitable configuration based on the objects
    internal state.

    @returns a source/sinks to job set map: SourceSinkSet->set(ChuckyJobs).
    """   
    def generate(self):
        if self.function_name:
            configurations=self.genJobsForFunc(self.function_name)  
        else:
            func_job_map=dict()
            if self.callee_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.callee_names,CALLEE,func_job_map)
                if len(func_job_map)==0:return False,dict()
            if self.parameter_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.parameter_names,PARAMETER,func_job_map)
                if len(func_job_map)==0:return False,dict()
            if self.variable_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.variable_names,VARIABLE,func_job_map)
                if len(func_job_map)==0:return False,dict()
            if len(func_job_map)==0:return False,dict()
            
            configurations=set()
            
            for job in func_job_map.values():
                js=job.split()
                configurations=configurations.union(js)
            
        configurations = list(set(configurations))
        d=self.generate_sourcesinks_job_map(configurations)
        if not self.function_name:
            for configs in d.values():
                for config in configs:
                    config.setJobSet(configs)
                    
        if self.limit:
            #limit option can only limit the target analyse functions.
            #Note that limit option doesn't means to limit the neighborhoods selection scope.
            if self.limit.isdigit():
                configurations = list(set([c for c in configurations if int(self.limit) == c.function.node_id]))
            else:
                configurations = [c for c in configurations if re.search(self.limit, c.function.name)]
                return self.generate_sourcesinks_job_map(configurations)
        return d
    def generate_sourcesinks_job_map(self,jobs):
        d=dict()        
        for job in jobs:
            sourcesinks=job.sourcesinks
            if sourcesinks not in d:
                d[sourcesinks]=set()
            d[sourcesinks].add(job)
        return d
        
