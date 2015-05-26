from job.Symbol import Symbol

PARAMETER = 'Parameter'
VARIABLE = 'Variable'
CALLEE = 'Callee'

class SourceSinkSet:
    
    def __init__(self,callee_set=set(),parameter_set=set(),variable_set=set()):
        
        self.callee_set=callee_set.copy()
        self.parameter_set=parameter_set.copy()
        self.variable_set=variable_set.copy()
        
    def getSingleSource(self):
        for c in self.callee_set:
            return c
        for p in self.parameter_set:
            return p
        for v in self.variable_set:
            return v
        
    def getAllInOneSet(self):
        symbols=self.callee_set.union(self.parameter_set).union(self.variable_set)
        return symbols
    
    def addToCalleeSet(self,callee):
        self.callee_set.add(callee)
           
    def addToParameterSet(self,parameter):
        
        self.parameter_set.add(parameter)
        
    def addToVariableSet(self,variable):
        self.variable_set.add(variable)
        
    def nameDict(self,source_sink_set):
        d=dict()
        for c in source_sink_set:
            if c.target_name not in d:
                d[c.target_name]=set()
            d[c.target_name].add(c)
        return d
    
    def generateCombinationList(self,cd):
        itemlist=[]
        for s in cd.values():
            if len(itemlist)==0:
                for c in s:
                    itemlist.append(set([c]))
            else:
                tmp=[]
                for item in itemlist:
                    for c in s:
                        tmp.append(item.union(set([c])))
                itemlist=tmp
        return itemlist
    def genCombination(self):
        cd=self.nameDict(self.callee_set)
        pd=self.nameDict(self.parameter_set)
        vd=self.nameDict(self.variable_set)
        c_itemset=self.generateCombinationList(cd)
        p_itemset=self.generateCombinationList(pd)
        v_itemset=self.generateCombinationList(vd)
        return c_itemset,p_itemset,v_itemset
    
    def addSourceSinkByString(self,code,decl_type,identifierType):
        symbol = Symbol()
        symbol.setName(code)
        symbol.setType(identifierType)
        symbol.setDeclType(decl_type)
        if identifierType == CALLEE:
            self.addToCalleeSet(symbol)
        elif identifierType == PARAMETER:           
            self.addToParameterSet(symbol)
        elif identifierType == VARIABLE:            
            self.addToVariableSet(symbol)
        else: raise Exception(identifierType,'This source type is Unsupported!!')        
            
    def addSourceSinkByDBIdentifier(self,db_identifier,identifierType):
        if identifierType == CALLEE:
            self.addSourceSinkByString(db_identifier.code,db_identifier.function(),CALLEE)
        elif identifierType == PARAMETER:
            self.addSourceSinkByString(db_identifier.code,db_identifier.declaration_type(),PARAMETER)
        elif identifierType == VARIABLE:
           self.addSourceSinkByString(db_identifier.code,db_identifier.declaration_type(),VARIABLE)
        else: raise Exception(identifierType,'This source type is Unsupported!!')
        
           
    def __hash__(self):
        h=0
        for callee in self.callee_set:
            h=h^hash(callee)
        for parameter in self.parameter_set:
            h=h^hash(parameter)
        for variable in self.variable_set:
            h=h^hash(variable)
        return h
    
    def __eq__(self,other):
        if self.callee_set==other.callee_set and self.parameter_set==other.parameter_set and self.variable_set==other.variable_set:
            return True
        else:
            return False
        
    @staticmethod
    def SourceSinksToString(symbol_set):
        s=''
        start=False
        for symbol in symbol_set:
            if start:
                s=s+','
            if symbol.target_type==CALLEE:
                s=s+symbol.target_name+'['+symbol.target_type+']'
            else:
                s=s+symbol.target_decl_type+' '+symbol.target_name+'['+symbol.target_type+']'
            start=True
        return s
    
    def __str__(self):
        ss=list(self.callee_set)+list(self.parameter_set)+list(self.variable_set)
        return SourceSinkSet.SourceSinksToString(ss)