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
        self.function = function
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
            parameters = map(lambda x : (x.code, x.declaration_type()), parameters)
            parameters = set(parameters)
            for parameter, parameter_type in parameters:
                job=ChuckyJob(function)
                job.addSourceSinkByString(parameter,parameter_type,PARAMETER)
                configurations.append(job)
            variables = function.variables()
            variables = map(lambda x : (x.code, x.declaration_type()), variables)
            variables = set(variables)
            for variable, variable_type in variables:
                job=ChuckyJob(function)            
                job.addSourceSinkByString(variable,variable_type,VARIABLE)
                configurations.append(job)
            callees = function.callees()
            callees = map(lambda x : x.code, callees)
            callees = set(callees)
            for callee in callees:
                job=ChuckyJob(function)
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
    '''
    If the there is no identifier instances added, then add the instances of first encounterd meta-identifier all into the func_job_map.
    A meta-identifier is the abstract type with three key property:
    DECLAEATION_TYPE,    SOURCE_SINK_TYPE,    SOURCE_SINK_TYPE.
    
    Later,we will pick the intersection using the following instances of other meta-identifier
    '''
    def addFirstSourceSinkToEmptyDict(self,db_identifiers,identifier_type,func_job_map):
        #process same type identifier
        at_least_one=False
        for db_identifier in db_identifiers:#same name identifier
            job=ChuckyJob(db_identifier.function(),True)
            job.addSourceSinkByDBIdentifier(db_identifier,identifier_type)
            func_job_map[db_identifier.function()]=job
            at_least_one=True
        return at_least_one
    
    '''
    Given the source/sink name generate a map from function to job
    in which the function is the Symbol User and the job is the unsplited mixjob(That means identifiers with the same name and the same SOURCE/SINK_TYPE and different declaration type may be be add in the set together).
    '''
    def getFuncJobMapBySourceSinkNames(self,identifierNames,identifier_type,func_job_map):
        #process same type identifier
        have_source_sinks=self.test_and_sanitize_map_have_values(func_job_map)
            
        for identifier_name in identifierNames:
            #different name identifier
            db_identifiers = self.getIdentiferInstances(identifier_name,identifier_type)
            if not have_source_sinks:
                have_source_sinks=self.addFirstSourceSinkToEmptyDict(db_identifiers,identifier_type,func_job_map)
                
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
        if self.function:
            needcache=False
            configurations=self.genJobsForFunc(self.function)  
        else:
            needcache=True
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
        d=dict()        
        for config in configurations:
            sourcesinks=config.sourcesinks
            if sourcesinks not in d:
                d[sourcesinks]=set()
            d[sourcesinks].add(config)
            
        if not self.function:
            for configs in d.values():
                for config in configs:
                    config.setJobSet(configs)
                    
        if self.limit:
            if self.limit.isdigit():
                configurations = list(set([c for c in configurations if int(self.limit) == c.function.node_id]))
            else:
                configurations = [c for c in configurations if re.search(self.limit, c.function.name)]
            limitd=dict() 
            for config in configurations:
                sourcesinks=config.sourcesinks
                if sourcesinks not in limitd:
                    limitd[sourcesinks]=set()
                    limitd[sourcesinks].add(config)
            return needcache,limitd
        else:
            return needcache,d
