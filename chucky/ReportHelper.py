import os
import shutil
from py2neo.server import GraphServer
DEFALUT_REPORT_PATH='report'
'''
Need the $NEO4J_HOME environment variable to be set to the install path of Neo4j.
'''
class ReportHelper:
    parent_location=None
    def __init__(self,function,nearestNeighbors,report_path=DEFALUT_REPORT_PATH):
	self.function=function
	self.nearestNeighbors=nearestNeighbors
	self.report_path=report_path
    
    def getParentLocationOfDatabaseStore(self):
	server=GraphServer()#use the default path=$NEO4J_HOME
	db_location=server.conf.get("neo4j-server","org.neo4j.server.database.location")
	return os.path.abspath(os.path.join(db_location,os.pardir))
	
    def setScore(self,score):
	self.score=score
    def setFeature(self,feat):
	self.feat=feat
    def setSpecificity(self,spec):
	self.spec=spec
    def setMeanConditionCos(self,mcc):
	self.mcc=mcc
    def setConditionCosWithMean(self,ccm):
	self.ccm=ccm
    def setSemanticSimilarities(self,semantic_similarities):
	self.semantic_similarities=semantic_similarities
    def setFuncNameSimilarities(self,func_name_similarities):
	self.func_name_similarities=func_name_similarities
    def setFileNameSimilarities(self,file_name_ngram_similarities):
	self.file_name_similarities=file_name_ngram_similarities
    def setCallerSetSimilarities(self,caller_set_similarities):
	self.caller_set_similarities=caller_set_similarities
    def parseLocationString(self,string):
	x = string.split(':')
	for i in range(1,len(x)):
	    x[i] = int(x[i])
	return x
    def setSourceSinks(self,sourcesinks):
	self.sourcesinks=sourcesinks
    def generate(self):
	report_file=self.report_path+'/'+str(self.function)+'.c'
	self.clear_path(self.report_path,report_file)
	filehead=self.generateHead();
	content=''
	try:
	    for i in range(0,len(self.nearestNeighbors)):
		n=self.nearestNeighbors[i]
		s0=self.semantic_similarities[i]
		if hasattr(self,'func_name_similarities'):
		    s1=self.func_name_similarities[i]
		if hasattr(self,'file_name_similarities'):
		    s2=self.file_name_similarities[i]
		if hasattr(self,'caller_set_similarities'):
		    s3=self.caller_set_similarities[i]
		location=n.location()
		x=self.parseLocationString(location)
		(filename, startLine, startPos, startIndex, stopIndex)=x
		if not ReportHelper.parent_location:
		    ReportHelper.parent_location=self.getParentLocationOfDatabaseStore()
		#fix un_absolute path
		if(filename[:1]!='/'):
		    source_file_path=ReportHelper.parent_location+'/'+filename
		
		source_file = open(source_file_path, 'rb')
		file_output = open(report_file,'a')			
		source_file.read(startIndex)
		chunk=source_file.read(stopIndex-startIndex+1)
		array=chunk.split('\n')
		if(i==0):
		    headinfo='=============Target Function ============\n'
		else:headinfo='==================Top '+str(i)+'==================\n'
		headinfo+='-----------------------------------------\n'
		headinfo+='function:\t'+str(n)+'\n'
		headinfo+='node id:\t'+n.node_id+'\n'
		headinfo+='location:\t'+n.location()+'\n'
		headinfo+='-----------------------------------------\n'
		headinfo+='relative distances\n'
		headinfo+='-----------------------------------------\n'
		headinfo+='semantic:\t{:3.2f}\n'.format(s0)
		if hasattr(self,'func_name_similarities'):
		    headinfo+='function name:\t{:3.2f}\n'.format(s1)
		if hasattr(self,'file_name_similarities'):
		    headinfo+='file name:\t{:3.2f}\n'.format(s2)
		if hasattr(self,'caller_set_similarities'):
		    headinfo+='caller set:\t{:3.2f}\n'.format(s3)
		    headinfo+='-----------------------------------------\n'
		    headinfo+='Note:2.00 means we don\'t calculate it or we don\'t care about it in this situation, especially for caller set distance.\n'
		headinfo+='-----------------------------------------\n\n'
		content+=headinfo
		line=startLine
		for e in array:
		    content+=str(line)+':'+e+'\n'
		    line+=1
	    file_output.write(filehead+content)
	    #print chunk
	finally:
	    source_file.close()
	    file_output.flush()
	    file_output.close()
	
    def generateHead(self):
	filehead='/*This file reports the Top-'+str(len(self.nearestNeighbors)-1)+' similarest function for '+str(self.function)+'('+str(self.function.node_id)+').*/\n'
	filehead+='-----------------------------------------\n'
	filehead+='sourcesinks:\t'+str(self.sourcesinks)+'\n'
	filehead+='-----------------------------------------\n'
	filehead+='Anomaly Score:\t{:3.2f}\n'.format(self.score) 
	filehead+='Missing feature:\t{}\n'.format(self.feat)
	if hasattr(self,'mcc'):
	    filehead+='mean cos of cond vector:\t{:3.2f}\n'.format(self.mcc)
	if hasattr(self,'ccm'):
	    filehead+='cos with mean cond vector:\t{:3.2f}\n'.format(self.ccm)
	if hasattr(self,'spec'):
	    filehead+='feature specificity:\t{:3.2f}\t(specificity of the significant feature from all features:spec=maxscore-(sum(allscore)-max_score)/(len(allscore)-1))\n'.format(self.spec)
	filehead+='-----------------------------------------\n'
	return filehead	
    def clear_path(self,report_path,report_file):
	if(not os.path.exists(report_path)):
	    os.makedirs(report_path)
	elif(os.path.exists(report_file)):
	    if(os.path.isdir(report_file)):
		shutil.rmtree(report_file)
	    else:
		os.remove(report_file)