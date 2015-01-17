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

    # Suggested improvement: see ChuckyJob
    
    '''def __init__(self, identifier,identifier_type,n_neighbors):
        self.identifier=identifier
        self.identifier_type=identifier_type
        self.n_neighbors = n_neighbors'''
    def __init__(self,function,callees,parameters,variables, n_neighbors):
        self.function = function
        self.callee_names = callees
        self.parameter_names = parameters        
        self.variable_names = variables
        self.n_neighbors = n_neighbors
        self.limit = None

    """
    Generates a suitable configuration based on the objects
    internal state.

    @returns a list of ConfigRecords.
    """
    def genJobsForFunc(self,identifier,n_neighbors):
        configurations = []
        functions = FunctionLookup.lookup_functions_by_name(identifier)
        for function in functions:
            parameters = function.parameters()
            parameters = map(lambda x : (x.code, x.declaration_type()), parameters)
            parameters = set(parameters)
            for parameter, parameter_type in parameters:
                job=ChuckyJob(function,n_neighbors)
                job.addSourceSinkByString(parameter,parameter_type,PARAMETER)
                configurations.append(job)
            variables = function.variables()
            variables = map(lambda x : (x.code, x.declaration_type()), variables)
            variables = set(variables)
            for variable, variable_type in variables:
                job=ChuckyJob(function,n_neighbors)            
                job.addSourceSinkByString(variable,variable_type,VARIABLE)
                configurations.append(job)
            callees = function.callees()
            callees = map(lambda x : x.code, callees)
            callees = set(callees)
            for callee in callees:
                job=ChuckyJob(function,n_neighbors)
                job.addSourceSinkByString(callee,function.name,CALLEE)
                configurations.append(job)
                
        return configurations
    
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
    def test_and_sanitize_map_have_values(self,func_job_map):
        for func,jobset in func_job_map.items():
            if jobset:
                return True;
            else:del func_job_map[func]
        return False
    def addFirstSourceSinkToEmptyDict(self,db_identifiers,identifier_type,func_job_map):
        at_least_one=False
        for db_identifier in db_identifiers:#same name callee
            job=ChuckyJob(db_identifier.function(),self.n_neighbors,True)
            job.addSourceSinkByDBIdentifier(db_identifier,identifier_type)
            func_job_map[db_identifier.function()]=job
            at_least_one=True
        return at_least_one
    
    def getFuncJobMapBySourceSinkNames(self,identifierNames,identifier_type,func_job_map):
        
        have_source_sinks=self.test_and_sanitize_map_have_values(func_job_map)
            
        for identifier_name in identifierNames:#different name callee
            db_identifiers = self.getIdentiferInstances(identifier_name,identifier_type)
            if not have_source_sinks:
                have_source_sinks=self.addFirstSourceSinkToEmptyDict(db_identifiers,identifier_type,func_job_map)
                
            else:
                tmp_map=dict()
                for db_identifier in db_identifiers:#same name callee 
                    if db_identifier.function() in func_job_map.keys():
                        job=func_job_map[db_identifier.function()]
                        job.addSourceSinkByDBIdentifier(db_identifier,identifier_type)
                        tmp_map[db_identifier.function()]=job
                if len(tmp_map)==0:return dict()
                else:func_job_map=tmp_map
                
        return func_job_map 
    
    def generate(self):
        if self.function:
            needcache=False
            configurations=self.genJobsForFunc(self.function,self.n_neighbors)  
        else:
            needcache=True
            #have_source_sink=False
            func_job_map=dict()
            if self.callee_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.callee_names,CALLEE,func_job_map)
                if len(func_job_map)==0:return dict()
            if self.parameter_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.parameter_names,PARAMETER,func_job_map)
                if len(func_job_map)==0:return dict()
            if self.variable_names:
                func_job_map=self.getFuncJobMapBySourceSinkNames(self.variable_names,VARIABLE,func_job_map)
                if len(func_job_map)==0:return dict()
            if len(func_job_map)==0:return dict()
            
            configurations=set()
            
            for job in func_job_map.values():
                js=job.split()
                configurations=configurations.union(js)
            
        configurations = list(set(configurations))
        
        if self.limit:
            if self.limit.isdigit():
                configurations = list(set([c for c in configurations if int(self.limit) == c.function.node_id]))
            else:
                configurations = [c for c in configurations if re.search(self.limit, c.function.name)]
                
        d=dict()        
        for config in configurations:
            sourcesinks=config.sourcesinks
            
            if sourcesinks not in d:
                d[sourcesinks]=set()
            d[sourcesinks].add(config)   
        
        for configs in d.values():
            for config in configs:
                config.setJobSet(configs)
        return needcache,d
            
        #fix duplicate
        #d=dict()
        #if parameter_names:
            #return
        #if self.identifier_type == 'callee':
            #d['callee']=set(configurations)
        #else:
            #for config in configurations:
                #if config.symbol not in d:
                    #d[config.symbol]=set()
                #d[config.symbol].add(config)             
        #return needcache,d
