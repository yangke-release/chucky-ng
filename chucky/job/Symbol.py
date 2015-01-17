PARAMETER = 'Parameter'
VARIABLE = 'Variable'
CALLEE = 'Callee'
class Symbol:
    def __init__(self):
        pass
    
    def setName(self, name):
        self.target_name = name

    def setType(self, aType):
        self.target_type = aType
    
    def __eq__(self, other):
        
        if  self.target_type==CALLEE:
            return self.target_type == other.target_type and\
                  self.target_name == other.target_name
       
        return self.target_name == other.target_name and\
            self.target_type == other.target_type and\
            self.target_decl_type == other.target_decl_type
    
    def __hash__(self):
        
        if  self.target_type==CALLEE:
            return hash(self.target_name) ^\
                   hash(self.target_type)
        
        return hash(self.target_name) ^\
            hash(self.target_type) ^\
            hash(self.target_decl_type)
    
    def __str__(self):
        return self.target_decl_type+' '+self.target_name+'['+self.target_type+']'
    
    def setDeclType(self, declType):
        self.target_decl_type = declType
