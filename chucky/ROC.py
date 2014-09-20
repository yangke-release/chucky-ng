#!/usr/bin/env python2
import os
import time
from chucky import Chucky
dbvar='org.neo4j.server.database.location'
dir='/home/yangke/Program/Fabian-Yamaguchi/evdata'
db='.joernIndex'
line='12'
projnames=['pidgin','libpng','tiff','firefox','linux' ]
symbolnames=['purple_base64_decode','length','dir','argc','dentry']
symboltypes=['Callee','Parameter','Parameter','Parameter','Parameter']

array1=['yahoo_process_status',
'yahoo_process_p2p',
'got_sessionreq',
'purple_ntlm_parse_type2',
'msim_msg_get_binary_from_element',
'digest_md5_handle_challenge',
'jabber_scram_feed_parser',
'parse_server_step1',
'scram_handle_success',
'msn_oim_report_to_user',
'msn_switchboard_show_ink',
'scram_handle_challenge',
'jabber_data_create_from_xml',
'do_buddy_avatar_update_data',
'jabber_vcard_parse_avatar',
'jabber_ibb_parse',
'jabber_vcard_save_mine',
'jabber_vcard_parse']
array2=['png_handle_sPLT',
'png_handle_sCAL',
'png_handle_tRNS',
'png_handle_bKGD',
'png_handle_pHYs',
'png_handle_oFFs',
'png_handle_tIME',
'png_handle_tEXt',
'png_handle_zTXt',
'png_handle_iTXt',
'png_handle_unknown',
'png_handle_IHDR',
'png_handle_PLTE',
'png_handle_IEND',
'png_handle_gAMA',
'png_handle_sBIT',
'png_handle_cHRM',
'png_handle_sRGB',
'png_handle_iCCP']
array3=['TIFFFetchString',
'TIFFFetchSubjectDistance',
'TIFFFetchByteArray',
'TIFFFetchShortArray',
'TIFFFetchShortPair',
'TIFFFetchLongArray',
'TIFFFetchPerSampleShorts',
'TIFFFetchPerSampleLongs',
'TIFFFetchPerSampleAnys']
array4=['PropertyOpForwarder',
'js :: array_sort',
'array_splice',
'array_slice',
'array_indexOfHelper',
'array_extra',
'LookupGetterOrSetter',
'DefineGetterOrSetter',
'array_unshift',
'array_concat']
'''
'array_join',
'array_push',
'js_Array']'''
array5=['jffs2_acl_setxattr','posix_acl_set','ocfs2_xattr_set_acl','generic_acl_set','ext4_xattr_set_acl','ext3_xattr_set_acl','ext2_xattr_set_acl','btrfs_xattr_acl_set']
li=[array1,array2,array3,array4,array5]
resultList=[]
for i in range(len(li)):
    #if i!=3 :continue
    projname=projnames[i]
    array=li[i]
    ROCs=dict()
    for fname in array:
        #if fname not in ['array_join','array_push','js_Array']:continue
        #if fname not in ['array_join']:continue
        result=open('neighbors/'+projname+'/'+fname.replace('js :: ',''),'r').readlines()
        TP=0
        FP=0
        TN=len(result)-len(array)
        FN=len(array)-1
        TPR_FPR=[]
        for j in range(len(result)):
            if j!=0:
                if result[j].split('\t')[0] in array and '/pds' not in result[j].split('\t')[1]:
                    TP+=1
                    FN-=1
                else:
                    FP+=1
                    TN-=1
            TPR_FPR.append([TP/float(TP+FN),FP/float(FP+TN)])
        ROCs[fname] = TPR_FPR 
     #AVG ROC
    accumulation=None
    for points in ROCs.values():
         if accumulation==None:
             accumulation=points
         else:
             for m in range(len(accumulation)):
                 accumulation[m][0]+=points[m][0]
                 accumulation[m][1]+=points[m][1]
    if accumulation:
        neighbor_result_path=projnames[i]+'-neighbors_ROC'
        #if not os.path.isdir(neighbor_result_path):
        #    os.makedirs(neighbor_result_path)
        f=open(neighbor_result_path,'w')
        for m in range(len(accumulation)):
             accumulation[m][0]=accumulation[m][0]/len(ROCs)
             accumulation[m][1]=accumulation[m][1]/len(ROCs)
             #s= str(m)+'\t'+str(accumulation[m][0])+'\t'+str(accumulation[m][1])+'\n'
             s= str(accumulation[m][1])+'\t'+str(accumulation[m][0])+'\n'
             print s
             f.write(s)
        f.close()
         
                
         
        
