from job.Job import ChuckyJob
from joernInterface.indexLookup.FunctionLookup import FunctionLookup
from joernInterface.indexLookup.IdentifierLookup import IdentifierLookup
from joernInterface.indexLookup.CalleeLookup import CalleeLookup
import re


PARAMETER = 'Parameter'
VARIABLE = 'Variable'
CALLEE = 'Callee'

"""
Creates a list of jobs for Chucky Engine based
on user queries.
"""

class JobGenerator(object):

    # Suggested improvement: see ChuckyJob
    
    def __init__(self, identifier, identifier_type, n_neighbors):
        self.identifier = identifier
        self.identifier_type = identifier_type
        self.n_neighbors = n_neighbors
        self.limit = None

    """
    Generates a suitable configuration based on the objects
    internal state.

    @returns a list of ConfigRecords.
    """
    
    def generate(self):
        configurations = []
        needcache=False
        if self.identifier_type == 'function':
            functions = FunctionLookup.lookup_functions_by_name(self.identifier)
            for function in functions:
                parameters = function.parameters()
                parameters = map(lambda x : (x.code, x.declaration_type()), parameters)
                parameters = set(parameters)
                for parameter, parameter_type in parameters:
                    configuration = ChuckyJob(
                            function,
                            parameter,
                            parameter_type,
                            PARAMETER,
                            self.n_neighbors)
                    configurations.append(configuration)
                variables = function.variables()
                variables = map(lambda x : (x.code, x.declaration_type()), variables)
                variables = set(variables)
                for variable, variable_type in variables:
                    configuration = ChuckyJob(
                            function,
                            variable,
                            variable_type,
                            VARIABLE,
                            self.n_neighbors)
                    configurations.append(configuration)
                callees = function.callees()
                callees = map(lambda x : x.code, callees)
                callees = set(callees)
                for callee in callees:
                    configuration = ChuckyJob(
                            function,
                            callee,
                            None,
                            CALLEE,
                            self.n_neighbors)
                    configurations.append(configuration)
        elif self.identifier_type == 'parameter':
            needcache=True
            parameters = IdentifierLookup.lookup_parameter(self.identifier)
            for parameter in parameters:
                configuration = ChuckyJob(
                        parameter.function(),
                        parameter.code,
                        parameter.declaration_type(),
                        PARAMETER,
                        self.n_neighbors,True)
                configurations.append(configuration)
        elif self.identifier_type == 'variable':
            needcache=True
            variables = IdentifierLookup.lookup_variable(self.identifier)
            for variable in variables:
                configuration = ChuckyJob(
                        variable.function(),
                        variable.code,
                        variable.declaration_type(),
                        VARIABLE,
                        self.n_neighbors,True)
                configurations.append(configuration)
        elif self.identifier_type == 'callee':
            needcache=True
            callees = CalleeLookup.calleesByName(self.identifier)
            for callee in callees:
                configuration = ChuckyJob(
                        callee.function(),
                        callee.code,
                        callee.function().name ,
                        CALLEE,
                        self.n_neighbors,True)
                configurations.append(configuration)

        
        #configurations = list(set(configurations))
        
        if self.limit:
            if self.limit.isdigit():
                configurations = list(set([c for c in configurations if int(self.limit) == c.function.node_id]))
            else:
                configurations = [c for c in configurations if re.search(self.limit, c.function.name)]
        #fix duplicate
        d=dict()
        for config in configurations:
            if not d.has_key(config.symbol):
                d[config.symbol]=set()
            d[config.symbol].add(config)
            
        #configurations=[]  
        #for configs in d.values():
            #configurations+=list(configs)             
        return (needcache,d)
