# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:37:45 2024

@author: wyuanc
"""

"""Basic behavior-element implementations for perception, memory, decision, motor processes in the QN-MHP model."""

import random

from gui_general import anim
from animation_general import entity_animation
from utility import color_dic
from model import server_def as s
from gui_general import Tasklist_dic
import math
from gui_general import task_info_dic
import time
import numpy as np             
        
import utility as u
#4.7 BEs


STW_record = {}    
copy_dic={}
eyefixation_dic={} 
neweyefixation = [0,0]
communication_signal=0
eyefixation=[0,0]


animation = entity_animation()

ji_store_dic={}
jm_store_dic={}
ji_result_dic={}
jm_result_dic={}
count_num_dic={}
cal_sd_num_dic={}
cal_sd_result_dic={}

def See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    if attribute['type']==2:  
        global communication_signal,eyefixation
        if anim==1:
            #If visual entity arrives, See is enabled
            print('%.2fmsec, See BE is enabled by the arrival of visual entity #%s'%(env.now,(i[0],k)))
    
            #At server1: 
            #Visual input at server1: 
            #If receiving a communication signal from serverW, update eye fixation location
           
            if communication_signal == 1:
                eyefixation = neweyefixation
                communication_signal = 0   #updating ends, flip the communication signal sign
            #print('eye fixation input at server1: ',eyefixation)
            
            #if entity (i) is Noise, no entry 
            #(for now, no need to go to Server 2, TBD later)
    
            if attribute['stimuli'] == 0:
                print('entity', (i[0],k), 'is a noise')
            #if entity (i) is Visual Signal (of any kind): 
            else: 
                print('entity', (i[0],k), 'is a visual signal')
    
                animation.enter(qn_mhp.server1, '1','0_1', i, j, k,generation)  
                animation.add('1', i, j, k,generation)                
                yield env.timeout(ppt)  #use ppt time
                animation.delete(i, j, k, '1',generation)
                #update deaprture number of server
                u.departure_server_N ['server1'][k]['time'].append(env.now)
                u.departure_server_N ['server1'][k]['number'].append(len(u.departure_server_N ['server1'][k]['time']))
                
                outserver_dic[1] = 1 #send entity (i) to server 2&3
            
            #At server2 & 3: 
            #if receiving entity (i) from Server 1
            if outserver_dic[1] == 1:
                yield env.process(s().server2(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,animation,ppt,cpt,mpt))\
                    &env.process(s().server3(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,animation,ppt,cpt,mpt))              
                outserver_dic[2]=outserver_dic[3] = 1 #send entity (i) to server 4
                #update deaprture number of server
                u.departure_server_N ['server2'][k]['time'].append(env.now)
                u.departure_server_N ['server2'][k]['number'].append(len(u.departure_server_N ['server2'][k]['time']))
                #update deaprture number of server
                u.departure_server_N ['server3'][k]['time'].append(env.now)
                u.departure_server_N ['server3'][k]['number'].append(len(u.departure_server_N ['server3'][k]['time']))
                
            #At server4
            #If receiving entity (i) from server 2&3
            if outserver_dic[2] == 1 and outserver_dic[3]==1:          
                with qn_mhp.server4.request() as request:                
                    yield request     
                    animation.add('4', i, j, k,generation)             
                    yield env.timeout(ppt) #use ppt time   
                    animation.delete(i, j, k, '4',generation)
                    #update deaprture number of server
                    u.departure_server_N ['server4'][k]['time'].append(env.now)
                    u.departure_server_N ['server4'][k]['number'].append(len(u.departure_server_N ['server1'][k]['time']))
                  
            #send entity to  Server A and/or B
            #depending on whether it is Spatial and/or Verbal 
                if attribute['info'] == 4:  #if spatial 
                    outserver_dic[4] = 1  #send to A
                elif attribute['info'] == 5:  #if verbal
                    outserver_dic[4] = 2  #send to B
                elif attribute['info'] == 6:  #if both
                    outserver_dic[4] = 3  #send to both A and B
                elif attribute['info'] == 7: #if unknown or unspecified (by the modeler)
                    prob = random.uniform(0,1)
                    if prob <=0.5:  #send Entity (i) to Server A or B with equal probability (p=0.5) (for now)
                        outserver_dic[4] = 1 #send to A              
                    else:
                        outserver_dic[4] = 2 #send to B 
                
                # At Server A or B (the one that receives Entity (i)):
                #upon receiving entity (i) from Server 4:
                if outserver_dic[4]!=0:
                    #(immediately) send entity (i) to Server C, and keep a copy of entity (i)
                    outserver_dic[101] = outserver_dic[102]=1       
                    copy_dic[i[0]] = attribute
            
                    animation.enter(qn_mhp.serverC, 'C', '4_C', i, j, k, generation) 
                    animation.add('C', i, j, k,generation)  
                    animation.delete(i, j, k, 'C', generation)          
            print('%.2fmsec, See ends for entity #%s'%(env.now,(i[0],k))) 
        
        else:
            #If visual entity arrives, Watch_for is enabled
            print('%.2fmsec, See BE is enabled by the arrival of visual entity #%s'%(env.now,(i[0],k)))
        
            #At server1: 
            #Visual input at server1: 
            #If receiving a communication signal from serverW, update eye fixation location
    
            if communication_signal == 1:
                eyefixation = neweyefixation
                communication_signal = 0   #updating ends, flip the communication signal sign
            #print('eye fixation input at server1: ',eyefixation)
            
            #if entity (i) is Noise, no entry 
            #(for now, no need to go to Server 2, TBD later)
            if attribute['stimuli'] == 0:
                print('entity', (i[0],k), 'is a noise')
            #if entity (i) is Visual Signal (of any kind): 
            else: 
                print('entity', (i[0],k), 'is a visual signal')        
                yield env.timeout(ppt)  #use ppt time
        
                outserver_dic[1] = 1 #send entity (i) to server 2&3
            
            #At server2 & 3: 
            #if receiving entity (i) from Server 1
            if outserver_dic[1] == 1:
                yield env.process(s().server2(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))\
                    &env.process(s().server3(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))   
                outserver_dic[2]=outserver_dic[3] = 1 #send entity (i) to server 4
               
            #At server4
            #If receiving entity (i) from server 2&3
            if outserver_dic[2] == 1 and outserver_dic[3]==1:
            
                with qn_mhp.server4.request() as request:           
                    yield request            
                    yield env.timeout(ppt) #use ppt time   
                    
            #send entity to  Server A and/or B
            #depending on whether it is Spatial and/or Verbal 
                if attribute['info'] == 4:  #if spatial 
                    outserver_dic[4] = 1  #send to A
                elif attribute['info'] == 5:  #if verbal
                    outserver_dic[4] = 2  #send to B
                elif attribute['info'] == 6:  #if both
                    outserver_dic[4] = 3  #send to both A and B
                elif attribute['info'] == 7: #if unknown or unspecified (by the modeler)
                    prob = random.uniform(0,1)
                    if prob <=0.5:  #send Entity (i) to Server A or B with equal probability (p=0.5) (for now)
                        outserver_dic[4] = 1 #send to A              
                    else:
                        outserver_dic[4] = 2 #send to B 
                
                # At Server A or B (the one that receives Entity (i)):
                #upon receiving entity (i) from Server 4:
                if outserver_dic[4]!=0:
                    #(immediately) send entity (i) to Server C, and keep a copy of entity (i)
                    outserver_dic[101] = outserver_dic[102]=1       
                    copy_dic[i[0]] = attribute
                         
                print('%.2fmsec, See ends for entity #%s'%(env.now,(i[0],k))) 
        
            
        # in case user forgot to selcet 'Store to wm' BE
        if ['Store_to_WM']  not in Tasklist_dic[k]:
            yield env.process(Store_to_WM(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))
            
        #update departure number
        u.departure_BE_N['See'][k]=i[0]
        
def Hear (qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
    

    if attribute['type']==3:
        
        
        if anim==1:
          
           #If auditory entity arrives, Listen_to is enabled
           print('%.2fmsec, Hear BE is enabled by the arrival of entity #%s'%(env.now,(i[0],k)))
    
           #At server5: 
           #if entity (i) is Noise, no entry 
           #(for now, no need to go to Server 6, TBD later)
           if attribute['stimuli'] == 0:
               print('entity', (i[0],k), 'is a noise')
           #if entity (i) is Visual Signal (of any kind): 
           else: 
               print('entity', (i[0],k), 'is an auditory signal')
               
               animation.enter(qn_mhp.server5, '5','0_5' ,i, j, k,generation)           
               animation.add('5', i, j, k,generation)          
               yield env.timeout(ppt)  #use ppt time
               animation.delete(i, j, k, '5',generation)
               #update deaprture number of server
               u.departure_server_N ['server5'][k]['time'].append(env.now)
               u.departure_server_N ['server5'][k]['number'].append(len(u.departure_server_N ['server5'][k]['time']))
               
               outserver_dic[5] = 1 #send entity (i) to server 6&7
           
           #At server6 & 7: 
           #if receiving entity (i) from Server 5
           if outserver_dic[5] == 1:
               yield env.process(s().server6(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))\
                   &env.process(s().server7(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))              
           
            
               outserver_dic[6]=outserver_dic[7]=1
               #update deaprture number of server
               u.departure_server_N ['server6'][k]['time'].append(env.now)
               u.departure_server_N ['server6'][k]['number'].append(len(u.departure_server_N ['server6'][k]['time']))
               #update deaprture number of server
               u.departure_server_N ['server7'][k]['time'].append(env.now)
               u.departure_server_N ['server7'][k]['number'].append(len(u.departure_server_N ['server7'][k]['time']))
               
               
               
           #At server8
           #If receiving entity (i) from server 6&7
           if outserver_dic[6] == 1 and outserver_dic[7]==1:
               
               with qn_mhp.server8.request() as request:              
                   yield request            
                   animation.add('8', i, j, k,generation)              
                   yield env.timeout(ppt) #use ppt time
                   animation.delete(i, j, k, '8',generation)
                   #update deaprture number of server
                   u.departure_server_N ['server8'][k]['time'].append(env.now)
                   u.departure_server_N ['server8'][k]['number'].append(len(u.departure_server_N ['server8'][k]['time']))
                   
           #send entity to  Server A and/or B
           #depending on whether it is Spatial and/or Verbal 
               if attribute['info'] == 4:  #if spatial 
                   outserver_dic[8] = 1  #send to A
               elif attribute['info'] == 5:  #if verbal
                   outserver_dic[8] = 2  #send to B
               elif attribute['info'] == 6:  #if both
                   outserver_dic[8] = 3  #send to both A and B
               elif attribute['info'] == 7: #if unknown or unspecified (by the modeler)
                   prob = random.uniform(0,1)
                   if prob <=0.5:  #send Entity (i) to Server A or B with equal probability (p=0.5) (for now)
                       outserver_dic[8] = 1 #send to A               
                   else:
                       outserver_dic[8] = 2 #send to B 
                       
               # At Server A or B (the one that receives Entity (i)):
               #upon receiving entity (i) from Server 8:
               if outserver_dic[8]!=0:
                   #(immediately) send entity (i) to Server C, and keep a copy of entity (i)
                   outserver_dic[101] = outserver_dic[102]=1       
                   copy_dic[(i[0],k)] = attribute
                  
                   animation.enter(qn_mhp.serverC, 'C', '8_C', i, j, k, generation) 
                   animation.add('C', i, j, k,generation)  
                   animation.delete(i, j, k, 'C', generation)
                   
               print('%.2fmsec, Hear ends for entity #%s'%(env.now,(i[0],k)))
    
    
        else:
           #If auditory entity arrives, Listen_to is enabled
           print('%.2fmsec, Hear BE is enabled by the arrival of auditory entity #%s'%(env.now,(i[0],k)))
       
           #At server5: 
           #if entity (i) is Noise, no entry 
           #(for now, no need to go to Server 6, TBD later)
           if attribute['stimuli'] == 0:
               print('entity', (i[0],k), 'is a noise')
           #if entity (i) is Visual Signal (of any kind): 
           else: 
               print('entity', (i[0],k), 'is an auditory signal')
                      
               yield env.timeout(ppt)  #use ppt time
    
               outserver_dic[5] = 1 #send entity (i) to server 6&7
           
           #At server6 & 7: 
           #if receiving entity (i) from Server 5
           if outserver_dic[5] == 1:
               yield env.process(s().server6(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))\
                   &env.process(s().server7(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))              
           
           #At server8
           #If receiving entity (i) from server 6&7
           if outserver_dic[6] == 1 and outserver_dic[7]==1:
               
               with qn_mhp.server8.request() as request:
                      
                   yield request
            
                   yield env.timeout(ppt) #use ppt time
                        
                   
           #send entity to  Server A and/or B
           #depending on whether it is Spatial and/or Verbal 
               if attribute['info'] == 4:  #if spatial 
                   outserver_dic[8] = 1  #send to A
               elif attribute['info'] == 5:  #if verbal
                   outserver_dic[8] = 2  #send to B
               elif attribute['info'] == 6:  #if both
                   outserver_dic[8] = 3  #send to both A and B
               elif attribute['info'] == 7: #if unknown or unspecified (by the modeler)
                   prob = random.uniform(0,1)
                   if prob <=0.5:  #send Entity (i) to Server A or B with equal probability (p=0.5) (for now)
                       outserver_dic[8] = 1 #send to A               
                   else:
                       outserver_dic[8] = 2 #send to B 
                       
               # At Server A or B (the one that receives Entity (i)):
               #upon receiving entity (i) from Server 8:
               if outserver_dic[8]!=0:
                   #(immediately) send entity (i) to Server C, and keep a copy of entity (i)
                   outserver_dic[101] = outserver_dic[102]=1       
                   copy_dic[(i[0],k)] = attribute
                   
               print('%.2fmsec, Hear ends for entity #%s'%(env.now,(i[0],k)))

        # in case user forgot to selcet 'Store to wm' BE
        if not any('Store_to_WM' in sublist for sublist in Tasklist_dic[k]):
            yield env.process(Store_to_WM(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt))
            
        #update departure number
        u.departure_BE_N['Hear'][k]=i[0]
        
        
def Store_to_WM(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
    
    if Tasklist_dic[k]==  [['See'], ['Store_to_WM']] or  Tasklist_dic[k]==[['Hear'], ['Store_to_WM']] or   Tasklist_dic[k]==[['See','Hear'], ['Store_to_WM']]:    #if the task is Rememebr in WM 
        prio=i[0]*-1
       
    else:
        prio=-10e5
        
    if anim==1:
        #Store_to_STM is enabled if receiving entity (i) from Server 4 and/or Server 8
        if outserver_dic[4] !=0 or outserver_dic[8]!=0:
            print('%.2fmsec, Store_to_STM BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
        
            if outserver_dic[4]==1 or outserver_dic[8]==1:  #if entity is sent to serverA
                #At serverA
                yield env.process(s().serverA(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
                #update deaprture number of server
                u.departure_server_N ['serverA'][k]['time'].append(env.now)
                u.departure_server_N ['serverA'][k]['number'].append(len(u.departure_server_N ['serverA'][k]['time']))                    
            elif outserver_dic[4] == 2 or outserver_dic[8]==2: #if entity is sent to serverB            
                #At serverB
                yield env.process(s().serverB(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
                #update deaprture number of server
                u.departure_server_N ['serverB'][k]['time'].append(env.now)
                u.departure_server_N ['serverB'][k]['number'].append(len(u.departure_server_N ['serverB'][k]['time']))                       
            elif outserver_dic[4] == 3 or outserver_dic[8]==3: #if entity is sent to both serverA &B
            
            #At serverA&B
                yield env.process(s().serverA(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))\
                    & env.process(s().serverB(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
                #update deaprture number of server
                u.departure_server_N ['serverA'][k]['time'].append(env.now)
                u.departure_server_N ['serverA'][k]['number'].append(len(u.departure_server_N ['serverA'][k]['time']))
                #update deaprture number of server
                u.departure_server_N ['serverB'][k]['time'].append(env.now)
                u.departure_server_N ['serverB'][k]['number'].append(len(u.departure_server_N ['serverB'][k]['time']))
            print('%.2fmsec, Store_to_STM ends for entity #%s'%(env.now,(i[0],k)))
            
    else:
        #Store_to_STM is enabled if receiving entity (i) from Server 4 and/or Server 8
        if outserver_dic[4] !=0 or outserver_dic[8]!=0:
            print('%.2fmsec, Store_to_STM BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
        
            if outserver_dic[4]==1 or outserver_dic[8]==1:  #if entity is sent to serverA
        
                #At serverA
                yield env.process(s().serverA(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
       
            elif outserver_dic[4] == 2 or outserver_dic[8]==2: #if entity is sent to serverB            
                #At serverB
                yield env.process(s().serverB(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
                                 
            elif outserver_dic[4] == 3 or outserver_dic[8]==3: #if entity is sent to both serverA &B
            
            #At serverA&B
                yield env.process(s().serverA(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))\
                    & env.process(s().serverB(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, prio,generation,ppt,cpt,mpt))
                       
            print('%.2fmsec, Store_to_STM ends for entity #%s'%(env.now,(i[0],k)))
    
    #update departure number
    u.departure_BE_N['Store_to_WM'][k]=i[0]
    
def Choice(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt,**kwargs):
    
    if not kwargs:
        from gui_basic_BE import choice_N
        N=choice_N[k]
    else:
        N = kwargs['choice_N']
    
    #if no see or hear entity
    if len(Tasklist_dic[k])==1 and Tasklist_dic[k][0]==['Choice']:
        outserver_dic[4] = 1
       
    if anim==1:
        #Choice is enabled if receiving entity (i) from Server A or B  
        #if outserver_dic[101] == 1 and outserver_dic[102] == 1:
            print('%.2fmsec, Choice BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
            
            #At serverC 
            if outserver_dic[4]!=0 or outserver_dic[8]!=0:
                if outserver_dic[4]!=0:
                    animation.enter(qn_mhp.serverC, 'C', '4_C', i, j, k,generation)
                else:
                    animation.enter(qn_mhp.serverC, 'C', '8_C', i, j, k,generation)
                with qn_mhp.serverC.request() as request:               
                    yield request                
                    animation.add('C', i, j, k,generation)                    
                    yield env.timeout(cpt)
                    animation.delete(i, j, k, 'C',generation)
                #update deaprture number of server
                u.departure_server_N ['serverC'][k]['time'].append(env.now)
                u.departure_server_N ['serverC'][k]['number'].append(len(u.departure_server_N ['serverC'][k]['time']))
                #At serverF       
                #Use total time =cpt time + b* log2 (N) (N is the number of choices, b=50ms, for now) 
                b=150
                animation.enter(qn_mhp.serverF, 'F', 'C_F', i, j, k,generation)
                with qn_mhp.serverF.request() as request:        
                    yield request                
                    animation.add('F', i, j, k,generation)                
                    yield env.timeout(cpt+b*math.log(N,2))
                    animation.delete(i, j, k, 'F',generation)
                    #update deaprture number of server
                    u.departure_server_N ['serverF'][k]['time'].append(env.now)
                    u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))                            
                #Send entity (i) (back) to Server C; At Server C,
                outserver_dic[103] = 1  #send entity (i) to W
                print('%.2fmsec, Choice ends for entity #%s'%(env.now,(i[0],k))) 
    
    else:    
        #Choice is enabled if receiving entity (i) from Server A or B  
        #if outserver_dic[101] == 1 and outserver_dic[102] == 1:
            print('%.2fmsec, Choice BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
            
            #At serverC  
            with qn_mhp.serverC.request() as request:
                            
                yield request
                yield env.timeout(cpt)
                            
            
            #At serverF       
            #Use total time =cpt time + b* log2 (N) (N is the number of choices, b=50ms, for now) 
            b=150
            with qn_mhp.serverF.request() as request:
                    
                yield request
                
                yield env.timeout(cpt+b*math.log(N,2))
                
            #Send entity (i) (back) to Server C; At Server C,
            outserver_dic[103] = 1  #send entity (i) to W
            print('%.2fmsec, Choice ends for entity #%s'%(env.now,(i[0],k))) 
    
    #update departure number
    u.departure_BE_N['Choice'][k]=i[0]

def Judge_identity (qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
        
    if ['Look_for'] in Tasklist_dic[k]:
        from gui_compound_BE import judgei_target_dic
    else:
        from gui_basic_BE import judgei_target_dic
            
    #judge= 'color'
    print('%.2fmsec,Judge_identity BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
    if anim==1:
        #Judge_identity is enabled if receiving entity (i) from Server A or B  
        #if outserver_dic[101] == 1 and outserver_dic[102] == 1:
            
        #At serverF
        # store its attributes
        ji_store_dic[(i[0]),k]=attribute
        #use cpt time (at least, for now, perhaps 150 msec is needed)
        animation.enter(qn_mhp.serverF, 'F', 'C_F', i, j, k,generation)
        with qn_mhp.serverF.request() as request:
            yield request
            animation.add('F', i, j, k, generation)
            time.sleep(0.1)
            yield env.timeout(cpt)
            animation.delete(i, j, k, 'F',generation)
            #update deaprture number of server
            u.departure_server_N ['serverF'][k]['time'].append(env.now)
            u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))
        if judgei_target_dic[str(k)]['identity']=='Text':
            if judgei_target_dic[str(k)]['value']==attribute['text']:
                ji_result_dic[(i[0],k)]='T'
                print('%.2fmsec,Judge_identity,target %s is found'%(env.now,judgei_target_dic[str(k)]['value']))
            else:
                ji_result_dic[(i[0],k)]='F'
                print('%.2fmsec,Judge_identity,target %s is not found'%(env.now,judgei_target_dic[str(k)]['value']))
  
                    
        elif judgei_target_dic[str(k)]['identity']=='Color':
            for (key,value) in color_dic.items():
                if key == judgei_target_dic[str(k)]['value']:
                    color = value
            if color==attribute['color']:
                ji_result_dic[(i[0],k)]='T'
                print('%.2fmsec,Judge_identity,target %s is found'%(env.now,judgei_target_dic[str(k)]['value']))
            else:
                ji_result_dic[(i[0],k)]='F'
                print('%.2fmsec,Judge_identity,target %s is not found'%(env.now,judgei_target_dic[str(k)]['value']))
        
    elif anim==0:
        #Judge_identity is enabled if receiving entity (i) from Server A or B  
        #if outserver_dic[101] == 1 and outserver_dic[102] == 1:
            
        #At serverF
        # store its attributes
        ji_store_dic[(i[0]),k]=attribute
        #use cpt time (at least, for now, perhaps 150 msec is needed)       
        with qn_mhp.serverF.request() as request:
            yield request
            yield env.timeout(cpt)

        if judgei_target_dic[str(k)]['identity']=='Text':
            if judgei_target_dic[str(k)]['value']==attribute['text']:
                ji_result_dic[(i[0],k)]='T'
                print('%.2fmsec,Judge_identity,target %s is found'%(env.now,judgei_target_dic[str(k)]['value']))
            else:
                ji_result_dic[(i[0],k)]='F'
                print('%.2fmsec,Judge_identity,target %s is not found'%(env.now,judgei_target_dic[str(k)]['value']))
  
                    
        elif judgei_target_dic[str(k)]['identity']=='Color':
            if eval(judgei_target_dic[str(k)]['value'])==attribute['color']:
                ji_result_dic[(i[0],k)]='T'
                print('%.2fmsec,Judge_identity,target %s is found'%(env.now,judgei_target_dic[str(k)]['value']))
            else:
                ji_result_dic[(i[0],k)]='F'
                print('%.2fmsec,Judge_identity,target %s is not found'%(env.now,judgei_target_dic[str(k)]['value']))
                
    #update departure number
    u.departure_BE_N['Judge_identity'][k]=i[0]

def Judge_relative_location (qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,dimension,cpt,ppt,mpt):
  
    print('%.2fmsec,Judge_relative_location BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
    #Judge_identity is enabled if receiving entity (i) from Server A or B  
    #if outserver_dic[101] == 1 and outserver_dic[102] == 1:
        
    #At serverF
    # store its attributes
    jm_store_dic[(i[0]),k]=attribute
    if anim==1:
        animation.enter(qn_mhp.serverF, 'F', 'C_F', i, j, k,generation)
    #use cpt time (at least, for now, perhaps 150 msec is needed)
    with qn_mhp.serverF.request() as request:
        yield request
        if anim==1:
            animation.add('F', i, j, k, generation)
        yield env.timeout(cpt)
        if anim==1:
            animation.delete(i, j, k, 'F',generation)
                #update deaprture number of server
    u.departure_server_N ['serverF'][k]['time'].append(env.now)
    u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))    
    if dimension==1:
        if attribute['eye_loc'][0]==attribute['eye_loc'][1]:
            jm_result_dic[(i[0],k)]='T'
            print('Cursor location = Target location')
        elif attribute['eye_loc'][0]<attribute['eye_loc'][1]:
            jm_result_dic[(i[0],k)]='Left'
            print('Cursor location > Target location')
        elif attribute['eye_loc'][0]>attribute['eye_loc'][1]:
            jm_result_dic[(i[0],k)]='Right'
            print('Cursor location < Target location')
    elif dimension==2:
        
        if attribute['eye_loc'][0]==attribute['eye_loc'][2]:
            jm_result_dic[(i[0],k)]='T'
            print('Cursor location_x = Target location_x')
        elif attribute['eye_loc'][0]<attribute['eye_loc'][2]:
            jm_result_dic[(i[0],k)]='Left'
            print('Cursor location_x > Target location_x')
        elif attribute['eye_loc'][0]>attribute['eye_loc'][2]:
            jm_result_dic[(i[0],k)]='Right'
            print('Cursor location_x < Target location_x')
   
        if attribute['eye_loc'][1]==attribute['eye_loc'][3]:
            jm_result_dic[(i[0],k)]='T'
            print('Cursor location_y = Target location_y')
        elif attribute['eye_loc'][1]<attribute['eye_loc'][3]:
            jm_result_dic[(i[0],k)]='Left'
            print('Cursor location_y > Target location_y')
        elif attribute['eye_loc'][1]>attribute['eye_loc'][3]:
            jm_result_dic[(i[0],k)]='Right'
            print('Cursor location_y < Target location_y')

    print('%.2fmsec,Judge_relative_location ends for entity #%s'%(env.now,(i[0],k)))
    #update departure number
    u.departure_BE_N['Judge_relative_location'][k]=i[0]
    
def Cal_single_digit_num(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
    
    from display_basic_BE import Reaction_calsingledig
    from gui_basic_BE import operation
    
    if anim== 1:
        #At serverF
        #Upon receiving entity#1 from Server A/B/C/… with attribute “number 1”,
        #Use cpt time,
        #Store entity#1’s “number 1” in related data structure of F;
        #Upon receiving entity#2 from Server A/B/C/… with attribute “number 2”,
        #Use cpt time,
        #Store entity#2’s “number 2” in related data structure of F
        animation.enter(qn_mhp.serverF, 'F', 'C_F', i, j, k,generation)
        with qn_mhp.serverF.request() as request:
            yield request
            animation.add('F', i, j, k, generation)
            yield env.timeout(cpt)
            animation.delete(i, j, k, 'F', generation)
            #update deaprture number of server
            u.departure_server_N ['serverF'][k]['time'].append(env.now)
            u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))
        
        if i[0]%2!=0:
            cal_sd_num_dic['num1']=attribute['cal_sd_num1']
            Reaction_calsingledig().first_num( cal_sd_num_dic['num1'])
            
        elif i[0]%2==0:
            cal_sd_num_dic['num2']=attribute['cal_sd_num2']
            Reaction_calsingledig().second_num(cal_sd_num_dic['num2'])
            #use cpt time
            # Generate New Entity#F(i) with attribute “Result”,
            #Use cpt time
            #Result = the corresponding arithmetic calculation result for Entity 1 and Entity 2
            #Use cpt time,
            #Store Result in related data structure
            animation.enter(qn_mhp.serverF, 'F', 'C_F', i, j, k,generation)
            with qn_mhp.serverF.request() as request:
                yield request
                animation.add('F', i, j, k, generation)
                yield env.timeout(2*cpt)
                animation.delete(i, j, k, 'F',generation)
                #update deaprture number of server
                u.departure_server_N ['serverF'][k]['time'].append(env.now)
                u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))
            if operation=='Add (+)':
                cal_sd_result_dic[i[0]]=cal_sd_num_dic['num1']+cal_sd_num_dic['num2']
                print('Result:',cal_sd_num_dic['num1'],'+',cal_sd_num_dic['num2'],'=',cal_sd_result_dic[i[0]])
            elif operation=='Subtract (-)':
                cal_sd_result_dic[i[0]]=(cal_sd_num_dic['num1']-cal_sd_num_dic['num2'])
                print('Result:',cal_sd_num_dic['num1'],'-',cal_sd_num_dic['num2'],'=',cal_sd_result_dic[i[0]])
            elif operation == 'Multiplication (*)':
                cal_sd_result_dic[i[0]]=(cal_sd_num_dic['num1']*cal_sd_num_dic['num2'])
                print('Result:',cal_sd_num_dic['num1'],'*',cal_sd_num_dic['num2'],'=',cal_sd_result_dic[i[0]])
            elif operation=='Division (/)':
                cal_sd_result_dic[i[0]]=(cal_sd_num_dic['num1']/cal_sd_num_dic['num2'])
                print('Result:',cal_sd_num_dic['num1'],'/',cal_sd_num_dic['num2'],'=',cal_sd_result_dic[i[0]])
            attribute['cal_sd_result']=cal_sd_result_dic[i[0]]   
            print('%.2fmsec, Cal_sigle_digit_num ends for entity #%s'%(env.now,(i[0],k))) 
            Reaction_calsingledig().result(cal_sd_result_dic[i[0]])
            #Send entity#F1 to Server C
            #At serverC    
            Reaction_calsingledig().delete()
    elif anim==0:
        #At serverF
        #Upon receiving entity#1 from Server A/B/C/… with attribute “number 1”,
        #Use cpt time,
        #Store entity#1’s “number 1” in related data structure of F;
        #Upon receiving entity#2 from Server A/B/C/… with attribute “number 2”,
        #Use cpt time,
        #Store entity#2’s “number 2” in related data structure of F
        with qn_mhp.serverF.request() as request:
            yield request
            yield env.timeout(cpt)
        if i[0]==1:
            cal_sd_num_dic['num1']=attribute['cal_sd_num1']
        elif i[0]==2:
            cal_sd_num_dic['num2']=attribute['cal_sd_num2']
            #use cpt time
            # Generate New Entity#F(i) with attribute “Result”,
            #Use cpt time
            #Result = the corresponding arithmetic calculation result for Entity 1 and Entity 2
            #Use cpt time,
            #Store Result in related data structure
            with qn_mhp.serverF.request() as request:
                yield request
                yield env.timeout(3*cpt)
           
            if operation=='Add (+)':
                cal_sd_result_dic[i[0]]=cal_sd_num_dic['num1']+cal_sd_num_dic['num2']
            elif operation=='Subtract (-)':
                cal_sd_result_dic[i[0]](cal_sd_num_dic['num2']-cal_sd_num_dic['num1'])
            elif operation == 'Multiplication (*)':
                cal_sd_result_dic[i[0]](cal_sd_num_dic['num1']*cal_sd_num_dic['num2'])
            elif operation=='Division (/)':
                cal_sd_result_dic[i[0]](cal_sd_num_dic['num1']/cal_sd_num_dic['num2'])
            attribute['cal_sd_result']=cal_sd_result_dic[i[0]]   
            #Send entity#F1 to Server C
            #At serverC
    
    #update departure number
    u.departure_BE_N['Cal_single_digit_num'][k]=i[0]



# Choice + Mouse_click uses the same response-target display as Choice + Press_button.
# The mouse movement time remains calculated by Mouse_click (Fitts' law).
def _is_choice_mouse_click(task):
    return (any('Choice' in step for step in task)
            and any('Mouse_click' in step for step in task)
            and not any('Press_button' in step for step in task))

#for various press_button display background in different task scenarios
window={}
for k in Tasklist_dic:
    window[k]=None
    if ['Press_button'] in Tasklist_dic[k] or _is_choice_mouse_click(Tasklist_dic[k]):
        #simple reaction time or choice reaction time
        if any('Choice' in sublist for sublist in Tasklist_dic[k]):   
            from display_basic_BE import reaction_press_button
            from gui_general import entity_dic
            window[k] = reaction_press_button(k)
            #choose from multiple colors or texts
            for r in range(2,6):
                if entity_dic[(r,1,str(k))] == 'Text':
                    window[k].background('text')
                elif entity_dic[(r,1,str(k))] == 'Color':
                    window[k].background('color')
                break
            
        
def Press_button(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
    if anim==1:
        #Press_button is enabled if receiving entity (i) from Server C  
        #if outserver_dic[103] == 1:
            print('%.2fmsec, Press_button BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
               
            #At serverW:  
            animation.enter(qn_mhp.serverW, 'W', 'C_W', i, j, k,generation)
            with qn_mhp.serverW.request() as request:
                yield request
                
                animation.add('W', i, j, k,generation)
                
                yield env.timeout(mpt)  #use mpt time
                animation.delete(i, j, k, 'W',generation)
                #update deaprture number of server
                u.departure_server_N ['serverW'][k]['time'].append(env.now)
                u.departure_server_N ['serverW'][k]['number'].append(len(u.departure_server_N ['serverW'][k]['time']))
            outserver_dic[201] = 1  #Send entity (i) to Server Y 
        
        #At serverY
        #If receiving entity (i) from Server W
        #if outserver_dic[201] == 1:
            animation.enter(qn_mhp.serverY, 'Y', 'W_Y', i, j, k,generation)
            with qn_mhp.serverY.request() as request:                         
                yield request                
                animation.add('Y', i, j, k,generation)
                yield env.timeout(mpt) #Use mpt time
                animation.delete(i, j, k, 'Y',generation)
                #update deaprture number of server
                u.departure_server_N ['serverY'][k]['time'].append(env.now)
                u.departure_server_N ['serverY'][k]['number'].append(len(u.departure_server_N ['serverY'][k]['time']))
                
            outserver_dic[202] = 1   #Send entity (i) to Server Z 
            
        #At serverZ
        #If receiving entity (i) from Server Y
        #if outserver_dic[202] == 1:
            animation.enter(qn_mhp.serverZ, 'Z', 'Y_Z', i, j, k,generation)
            with qn_mhp.serverZ.request() as request:
                
                yield request
                
                animation.add('Z', i, j, k,generation)
                
                yield env.timeout(mpt) #Use mpt time
                animation.delete(i, j, k, 'Z',generation)
                #update deaprture number of server
                u.departure_server_N ['serverZ'][k]['time'].append(env.now)
                u.departure_server_N ['serverZ'][k]['number'].append(len(u.departure_server_N ['serverZ'][k]['time']))
            outserver_dic[203] = 1  #Send entity (i) to Finger Server  
        
        #At lefthand server
        #If receiving entity (i) from Server Z 
        #if outserver_dic[203] == 1:
            animation.enter(qn_mhp.lefthand, '22', 'Z_22', i, j, k,generation)
            with qn_mhp.lefthand.request() as request:
                
                yield request
                
                animation.add('22', i, j, k,generation)
                
                yield env.timeout(20) # for now, use a constant, say 20 msec for “finger press physical action” time
                animation.delete(i, j, k, '22',generation)
                if window[k]:
                    window[k].add_button(i)
                #update deaprture number of server
                u.departure_server_N ['lefthand'][k]['time'].append(env.now)
                u.departure_server_N ['lefthand'][k]['number'].append(len(u.departure_server_N ['lefthand'][k]['time']))
            print('%.2fmsec, Press_button ends for entity #%s'%(env.now,(i[0],k)))
    
    else:
        #Press_button is enabled if receiving entity (i) from Server C  
        if outserver_dic[103] == 1:
            print('%.2fmsec, Press_button BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
               
            #At serverW:  
            with qn_mhp.serverW.request() as request:
             
                yield request
    
                yield env.timeout(mpt)  #use mpt time
          
            outserver_dic[201] = 1  #Send entity (i) to Server Y 
        
        #At serverY
        #If receiving entity (i) from Server W
        if outserver_dic[201] == 1:
            with qn_mhp.serverY.request() as request:
               
                yield request
             
                yield env.timeout(mpt) #Use mpt time
               
            outserver_dic[202] = 1   #Send entity (i) to Server Z 
            
        #At serverZ
        #If receiving entity (i) from Server Y
        if outserver_dic[202] == 1:
            with qn_mhp.serverZ.request() as request:
                        
                yield request
                yield env.timeout(mpt) #Use mpt time
          
            outserver_dic[203] = 1  #Send entity (i) to Finger Server  
        
        #At lefthand server
        #If receiving entity (i) from Server Z 
        if outserver_dic[203] == 1:
            with qn_mhp.lefthand.request() as request:
                         
                yield request
               
                yield env.timeout(20) # for now, use a constant, say 20 msec for “finger press physical action” time
                           
            print('%.2fmsec, Press_button ends for entity #%s'%(env.now,(i[0],k)))
    
    #update departure number
    u.departure_BE_N['Press_button'][k]=i[0]
    
    
#This is for multitask scenarios, multiple windows will be open for multiple mouse click tasks
reaction_c = {}       
for k in Tasklist_dic:
    if ['Mouse_click'] in Tasklist_dic[k] and not _is_choice_mouse_click(Tasklist_dic[k]):
        #simple reaction time or choice reaction time
            from display_basic_BE import Reaction_click
            from gui_basic_BE import mouse_click_dimension_dic
            mouse_click_dimension = int(mouse_click_dimension_dic[k])
            reaction_c[k] = Reaction_click(mouse_click_dimension)
            
def Mouse_click(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt,**kwargs):
    
    print('%.2fmsec, Mouse_click BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))
        
    #At serverW:  
    with qn_mhp.serverW.request() as request:
     
        yield request

        yield env.timeout(mpt)  #use mpt time
  
    outserver_dic[201] = 1  #Send entity (i) to Server Y 
    #update deaprture number of server
    u.departure_server_N ['serverW'][k]['time'].append(env.now)
    u.departure_server_N ['serverW'][k]['number'].append(len(u.departure_server_N ['serverW'][k]['time']))
    #At serverY
    #If receiving entity (i) from Server W
    if outserver_dic[201] == 1:
        with qn_mhp.serverY.request() as request:
           
            yield request
         
            yield env.timeout(mpt) #Use mpt time
            #update deaprture number of server
            u.departure_server_N ['serverY'][k]['time'].append(env.now)
            u.departure_server_N ['serverY'][k]['number'].append(len(u.departure_server_N ['serverY'][k]['time']))
        outserver_dic[202] = 1   #Send entity (i) to Server Z 
        
    #At serverZ
    #If receiving entity (i) from Server Y
    if outserver_dic[202] == 1:
        with qn_mhp.serverZ.request() as request:
                    
            yield request
            yield env.timeout(mpt) #Use mpt time
            #update deaprture number of server
            u.departure_server_N ['serverZ'][k]['time'].append(env.now)
            u.departure_server_N ['serverZ'][k]['number'].append(len(u.departure_server_N ['serverZ'][k]['time']))
        outserver_dic[203] = 1  #Send entity (i) to Finger Server  
    
    #kwargs['dimension']:1d,2d,3d
    #kwargs['width']:W
    #kwargs['coords']: (cursor_x,target_x,cursor_y,target_y,cursor_z,target_z)
    # Shared, configurable Fitts' Law implementation for all mouse tasks.
    from mouse_movement_model import calculate_mouse_movement_time
    if kwargs:
        W=kwargs['width']
        if kwargs['dimension'] == '1d':      
            cursor_x = kwargs['coords'][0]
            target_x = kwargs['coords'][1]
            A=abs(cursor_x-target_x)
            MT = calculate_mouse_movement_time(A, W)
            yield env.timeout(MT) 
        elif kwargs['dimension'] == '2d': 
            #unit: mm in the real world
            cursor_x = kwargs['coords'][0]
            target_x = kwargs['coords'][1]
            cursor_y = kwargs['coords'][2]
            target_y = kwargs['coords'][3]
            A=np.sqrt((cursor_x-target_x)**2 + (cursor_y-target_y)**2)
            MT = calculate_mouse_movement_time(A, W)
            #At righthand server
            #If receiving entity (i) from Server Z 
            if outserver_dic[203] == 1:
                with qn_mhp.righthand.request() as request:                             
                    yield request

                    yield env.timeout(MT) 
                    #update deaprture number of server
                    u.departure_server_N ['righthand'][k]['time'].append(env.now)
                    u.departure_server_N ['righthand'][k]['number'].append(len(u.departure_server_N ['righthand'][k]['time']))
    else:
        
        choice_click = _is_choice_mouse_click(Tasklist_dic[k])
        if not choice_click:
            reaction_c[k].create_initial_point(attribute['eye_loc'],i[0])
        W=0.5
        #attribute['eye_loc']:[target_x,user_x,target_y,user_y,target_z,user_z]
        from gui_basic_BE import mouse_click_dimension_dic
        from gui_basic_BE import mouse_click_dimension_dic
        mouse_click_dimension = int(mouse_click_dimension_dic[k])
        if mouse_click_dimension == 1:
            cursor_x = attribute['eye_loc'][1]
            target_x = attribute['eye_loc'][0]
            print(f'from ({cursor_x},0) to ({target_x},0)')
            A = abs(cursor_x-target_x)

        elif mouse_click_dimension == 2:
            cursor_x = attribute['eye_loc'][1]
            target_x = attribute['eye_loc'][0]
            cursor_y = attribute['eye_loc'][3]
            target_y = attribute['eye_loc'][2]
            print(f'from ({cursor_x},{cursor_y}) to ({target_x},{target_y})')
            A = np.sqrt((cursor_x-target_x)**2 + (cursor_y-target_y)**2)
        
        elif mouse_click_dimension == 3:
            cursor_x = attribute['eye_loc'][1]
            target_x = attribute['eye_loc'][0]
            cursor_y = attribute['eye_loc'][3]
            target_y = attribute['eye_loc'][2]
            cursor_z = attribute['eye_loc'][5]
            target_z = attribute['eye_loc'][4]
            print(f'from ({cursor_x},{cursor_y},{cursor_z}) to ({target_x},{target_y},{target_z})')
            A = np.sqrt((cursor_x-target_x)**2 + (cursor_y-target_y)**2 + (cursor_z-target_z)**2)
        
        if choice_click and window.get(k):
            # Choice + Mouse_click: use the actual displayed button geometry.
            # Start at the last COMPLETED click (center on the first trial).
            # Independent Mouse_click keeps its original random coordinates.
            from mouse_click_layout import button_geometry, button_depth, get_start, complete_click
            from utility import color_list, text_list
            reaction_window = window[k]
            count = reaction_window.N
            if reaction_window.sti_type == 'color':
                selected = color_list.index(attribute['color']) if count > 1 else 0
            else:
                selected = text_list.index(attribute['text']) if count > 1 else 0
            if selected >= count:
                raise ValueError('Choice target is outside the configured button layout')
            target_x, target_y, button_w, button_h = button_geometry(
                selected, count, reaction_window.w, reaction_window.h, mouse_click_dimension)
            start_x, start_y = get_start(k, reaction_window.w, reaction_window.h)
            if mouse_click_dimension == 1:
                A = abs(target_x - start_x)
            elif mouse_click_dimension == 2:
                A = math.hypot(target_x - start_x, target_y - start_y)
            else:
                # A flat-screen target has z=0. Developers may configure
                # per-button depths in mouse_click_layout.button_depth().
                target_z = button_depth(selected, count)
                start_z = 0.0  # First trial / previous flat-screen click.
                A = math.sqrt((target_x - start_x)**2 +
                              (target_y - start_y)**2 + (target_z - start_z)**2)
            W = button_w
            print(f'Choice mouse click: start=({start_x:.1f},{start_y:.1f}), '
                  f'target=({target_x:.1f},{target_y:.1f}), width={W:.1f}')
        MT = calculate_mouse_movement_time(A, W)
        
        #At righthand server
        #If receiving entity (i) from Server Z 
        if outserver_dic[203] == 1:
            with qn_mhp.righthand.request() as request:                             
                yield request

                yield env.timeout(MT)  
        if choice_click:
            if window.get(k):
                complete_click(k, (target_x, target_y))
                window[k].add_button(i)
        else:
            reaction_c[k].move_point()
            reaction_c[k].delete_point()
            #reaction_c.root_1d.mainloop()
            
    print('%.2fmsec, Mouse_click ends for entity #%s'%(env.now,(i[0],k)))

    #update departure number
    u.departure_BE_N['Mouse_click'][k]=i[0]

def _standalone_look_at_task(task_number):
    """Check the current task, not other tasks present in the model."""
    try:
        return Tasklist_dic[task_number] == [['Look_at']]
    except (KeyError, TypeError, NameError):
        return False


def Look_at(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):   
    
    global communication_signal,neweyefixation
    
    if anim==1:
        #Look_At is enabled if receiving entity (i) from Server C(or any entity from CogNet, in general)
        #if outserver_dic[103] == 1:
        #print('%.2fmsec, Look_at BE is enabled by receiving entity #%s'%(env.now,(i,j,k)))
        yield env.timeout(0)
        print('%.2fmsec, Look_at BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))  
        #At serverW: 
        print("%.2fmsec, Look_at requests Server W for entity #%s" % (env.now, (i[0], k)))
        animation.enter(qn_mhp.serverW, 'W', 'C_W', i, j, k,generation)
        with qn_mhp.serverW.request() as request:           
            yield request           
            print("%.2fmsec, Look_at starts Server W for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
            animation.add('W', i, j, k, generation)         
            yield env.timeout(mpt)  #use mpt time           
        animation.delete( i, j, k,'W',generation)
        print("%.2fmsec, Look_at exits Server W for entity #%s" % (env.now, (i[0], k)))      
        outserver_dic[201] = 1  #Send entity (i) to Server Y 
        #update deaprture number of server
        u.departure_server_N ['serverW'][k]['time'].append(env.now)
        u.departure_server_N ['serverW'][k]['number'].append(len(u.departure_server_N ['serverW'][k]['time']))
    
    #At serverY
    #If receiving entity (i) from Server W
    #At serverY
    #If receiving entity (i) from Server W
        if outserver_dic[201] == 1:
            print("%.2fmsec, Look_at requests Server Y for entity #%s" % (env.now, (i[0], k)))
            animation.enter(qn_mhp.serverY, 'Y', 'W_Y', i, j, k,generation)
            with qn_mhp.serverY.request() as request:              
                yield request              
                print("%.2fmsec, Look_at starts Server Y for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
                animation.add('Y', i, j, k, generation)            
                yield env.timeout(mpt) #Use mpt time               
            animation.delete( i, j, k,'Y',generation)
            print("%.2fmsec, Look_at exits Server Y for entity #%s" % (env.now, (i[0], k)))          
            outserver_dic[202] = 1   #Send entity (i) to Server Z 
            #update deaprture number of server
            u.departure_server_N ['serverY'][k]['time'].append(env.now)
            u.departure_server_N ['serverY'][k]['number'].append(len(u.departure_server_N ['serverY'][k]['time']))
        if outserver_dic[202] == 1:
            print("%.2fmsec, Look_at requests Server Z for entity #%s" % (env.now, (i[0], k)))
            animation.enter(qn_mhp.serverZ, 'Z', 'Y_Z', i, j, k,generation)
            with qn_mhp.serverZ.request() as request:               
                yield request                
                print("%.2fmsec, Look_at starts Server Z for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
                animation.add('Z', i, j, k, generation)               
                yield env.timeout(mpt) #Use mpt time                
            animation.delete( i, j, k,'Z',generation)
            print("%.2fmsec, Look_at exits Server Z for entity #%s" % (env.now, (i[0], k)))           
            outserver_dic[203] = 1  #Send entity (i) to Eye Server        
            #update deaprture number of server
            u.departure_server_N ['serverZ'][k]['time'].append(env.now)
            u.departure_server_N ['serverZ'][k]['number'].append(len(u.departure_server_N ['serverZ'][k]['time']))
        #At Eye server
        #If receiving entity (i) from Server Z 
        if outserver_dic[203] == 1:
            #yield time
            # can use Normal Distribution (mean=30 msec, sd=10 msec)or 20, 30, 40 msec for short, medium, or long saccades)
            print("%.2fmsec, Look_at requests Eye Server for entity #%s" % (env.now, (i[0], k)))
            animation.enter(qn_mhp.eyes, '23', 'Z_23', i, j, k,generation)
            with qn_mhp.eyes.request() as request:
                yield request                
                print("%.2fmsec, Look_at starts Eye Server for entity #%s" % (env.now, (i[0], k)))
                animation.add('23', i, j, k, generation) 
                from eye_movement_model import prepare_eye_motion, complete_saccade
                eye_start, eye_target, amplitude, duration = prepare_eye_motion(attribute)
                if _standalone_look_at_task(k):
                    from display_basic_BE import Reaction_general
                    Reaction_general().show_look_at(eye_start, eye_target)
                if eye_target is not None:
                    print('Eye saccade: start=%s target=%s amplitude=%.2f deg duration=%.2f ms' %
                          (eye_start, eye_target, amplitude, duration))
                yield env.timeout(duration)
                if eye_target is not None:
                    complete_saccade(eye_target)  
                #update deaprture number of server
                u.departure_server_N ['eyes'][k]['time'].append(env.now)
                u.departure_server_N ['eyes'][k]['number'].append(len(u.departure_server_N ['eyes'][k]['time']))
            animation.delete(i, j, k, '23',generation)
            print("%.2fmsec, Look_at exits Eye Server for entity #%s" % (env.now, (i[0], k)))
                
            #Recording/updating new eye fixation location/direction   
    
            neweyefixation = eye_target if eye_target is not None else attribute['eye_loc']
            if _standalone_look_at_task(k):
                from display_basic_BE import Reaction_general
                Reaction_general().show_look_at(neweyefixation, None)
            eyefixation_dic[(i[0],k)] = neweyefixation    
            #send a “communications signal,” Note: this signal is not an internal QN entity”to device/environment       
            communication_signal = 1
            print('%.2fmsec, Look_at ends for entity #%s'%(env.now,(i[0],k)))         
        if not _standalone_look_at_task(k) and ('Look_at' in task_info_dic.values() or 'Look_for' in task_info_dic.values()):
            from display_basic_BE import Reaction_general
            Reaction_general().show_eye(neweyefixation[1], neweyefixation[0])
        
        

    else:
        #Look_At is enabled if receiving entity (i) from Server C(or any entity from CogNet, in general)
        print('%.2fmsec, Look_at BE is enabled by receiving entity #%s'%(env.now,(i[0],k)))  
        #At serverW:  
        print("%.2fmsec, Look_at enters Server W for entity #%s" % (env.now, (i[0], k)))
        with qn_mhp.serverW.request() as request:
        
            yield request
        
            yield env.timeout(mpt)  #use mpt time
   
        outserver_dic[201] = 1  #Send entity (i) to Server Y 
        u.departure_server_N["serverW"][k]["time"].append(env.now)
        u.departure_server_N["serverW"][k]["number"].append(len(u.departure_server_N["serverW"][k]["time"]))
        print("%.2fmsec, Look_at exits Server W for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
        
        #At serverY
        #If receiving entity (i) from Server W
        #At serverY
        #If receiving entity (i) from Server W
        if outserver_dic[201] == 1:
            print("%.2fmsec, Look_at enters Server Y for entity #%s" % (env.now, (i[0], k)))
            with qn_mhp.serverY.request() as request:
             
                yield request
                
                yield env.timeout(mpt) #Use mpt time
     
            outserver_dic[202] = 1   #Send entity (i) to Server Z 
            u.departure_server_N["serverY"][k]["time"].append(env.now)
            u.departure_server_N["serverY"][k]["number"].append(len(u.departure_server_N["serverY"][k]["time"]))
            print("%.2fmsec, Look_at exits Server Y for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
        
        if outserver_dic[202] == 1:
            print("%.2fmsec, Look_at enters Server Z for entity #%s" % (env.now, (i[0], k)))
            with qn_mhp.serverZ.request() as request:
    
                
                yield request
                yield env.timeout(mpt) #Use mpt time
     
            outserver_dic[203] = 1  #Send entity (i) to Eye Server        
            u.departure_server_N["serverZ"][k]["time"].append(env.now)
            u.departure_server_N["serverZ"][k]["number"].append(len(u.departure_server_N["serverZ"][k]["time"]))
            print("%.2fmsec, Look_at exits Server Z for entity #%s (MPT=%.2f ms)" % (env.now, (i[0], k), mpt))
             
        #At Eye server
        #If receiving entity (i) from Server Z 
        if outserver_dic[203] == 1:
            #yield time
            # can use Normal Distribution (mean=30 msec, sd=10 msec)or 20, 30, 40 msec for short, medium, or long saccades)
            print("%.2fmsec, Look_at enters Eye Server for entity #%s" % (env.now, (i[0], k)))
            with qn_mhp.eyes.request() as request:               
                yield request    
                from eye_movement_model import prepare_eye_motion, complete_saccade
                eye_start, eye_target, amplitude, duration = prepare_eye_motion(attribute)
                if _standalone_look_at_task(k):
                    from display_basic_BE import Reaction_general
                    Reaction_general().show_look_at(eye_start, eye_target)
                if eye_target is not None:
                    print('Eye saccade: start=%s target=%s amplitude=%.2f deg duration=%.2f ms' %
                          (eye_start, eye_target, amplitude, duration))
                yield env.timeout(duration)
                if eye_target is not None:
                    complete_saccade(eye_target) 
            u.departure_server_N["eyes"][k]["time"].append(env.now)
            u.departure_server_N["eyes"][k]["number"].append(len(u.departure_server_N["eyes"][k]["time"]))
            print("%.2fmsec, Look_at exits Eye Server for entity #%s" % (env.now, (i[0], k)))
              
            #Recording/updating new eye fixation location/direction   
    
            neweyefixation = eye_target if eye_target is not None else attribute['eye_loc']
            if _standalone_look_at_task(k):
                from display_basic_BE import Reaction_general
                Reaction_general().show_look_at(neweyefixation, None)
            eyefixation_dic[(i[0],k)] = neweyefixation    
            #send a “communications signal,” Note: this signal is not an internal QN entity”to device/environment       
            communication_signal = 1
            print('%.2fmsec, Look_at ends for entity #%s'%(env.now,(i[0],k)))   
    
    #update departure number
    u.departure_BE_N['Look_at'][k]=i[0]
            
def Count(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
    
    trial=i[0]
    
    from display_basic_BE import Reaction_count
    
    Reaction_count().trial(trial)

    if anim==1:
        if outserver_dic[4] !=0 or outserver_dic[8]!=0:
            
            #At serverC  
            if outserver_dic[4]!=0 or outserver_dic[8]!=0:
                if outserver_dic[4]!=0:
                    animation.enter(qn_mhp.serverC, 'C', '4_C', i, j, k,generation)
                else:
                    animation.enter(qn_mhp.serverC, 'C', '8_C', i, j, k,generation)
                with qn_mhp.serverC.request() as request:               
                    yield request                
                    animation.add('C', i, j, k,generation)                    
                    yield env.timeout(cpt)
                    animation.delete(i, j, k, 'C',generation)
                    #update deaprture number of server
                    u.departure_server_N ['serverC'][k]['time'].append(env.now)
                    u.departure_server_N ['serverC'][k]['number'].append(len(u.departure_server_N ['serverC'][k]['time']))
            print('%.2fmsec, Count BE is enabled by receiving entity #%s'%(env.now,(i[0],k)),'\n','Start number:',\
                  attribute['Start'],'End number:',attribute['End'])
        
            count_num_dic['start_num']=attribute['Start']
            count_num_dic['end_num']=attribute['End']
            
            Reaction_count().show(count_num_dic['start_num'], count_num_dic['end_num'])
            
            for item in range(count_num_dic['start_num'],count_num_dic['end_num']+1):
                animation.enter(qn_mhp.serverF, 'F', 'C_F', i,j,k,generation)
                with qn_mhp.serverF.request() as request:
                    yield request
                    animation.add('F', i,j,k, generation)
                    yield env.timeout(cpt)
                    animation.delete(i,j,k, 'F', generation)
                    #update deaprture number of server
                    u.departure_server_N ['serverF'][k]['time'].append(env.now)
                    u.departure_server_N ['serverF'][k]['number'].append(len(u.departure_server_N ['serverF'][k]['time']))
                    print('%.2fmsec'%(env.now),'current number is ',item)
                    Reaction_count().count_num(item)
                #Send entity#F(i) to Server C:
                animation.enter(qn_mhp.serverC, 'C', 'F_C', i,j,k,generation)
                with qn_mhp.serverC.request() as request:
                    yield request
                    animation.add('C', i,j,k, generation)
                    yield env.timeout(cpt)
                    current_num=item+1
                    animation.delete(i,j,k, 'C', generation)                                   
                    #update deaprture number of server
                    u.departure_server_N ['serverC'][k]['time'].append(env.now)
                    u.departure_server_N ['serverC'][k]['number'].append(len(u.departure_server_N ['serverC'][k]['time']))
                if current_num>count_num_dic['end_num']:
                    break
                    print('%.2fmsec, Count ends for _animation #%s'%(env.now,i[0]))
                    Reaction_count().delete()
    elif anim==0:
  
        #At serverF
        if outserver_dic[4] !=0 or outserver_dic[8]!=0:
            print('%.2fmsec, Count BE is enabled by receiving entity #%s'%(env.now,i[0]),'\n',\
                  attribute['Start'],'End number:',attribute['End'])
            count_num_dic['start_num']=attribute['Start']
            count_num_dic['end_num']=attribute['End']
            for item in range(count_num_dic['start_num'],count_num_dic['end_num']+1):
                with qn_mhp.serverF.request() as request:
                    yield request
                    yield env.timeout(cpt)
                    print('%.2fmsec'%(env.now),'current number is ',item)
    
                #Send entity#F(i) to Server C:                
                with qn_mhp.serverC.request() as request:
                    yield request
                    yield env.timeout(cpt)
                    current_num=item+1
                
                if current_num>count_num_dic['end_num']:
                    break
                    print('%.2fmsec, Count ends for entity #%s'%(env.now,i[0]))
    Reaction_count().delete()

    #update departure number
    u.departure_BE_N['Count'][k]=i[0]