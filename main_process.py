# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 12:00:32 2024

@author: wyuanc
"""

"""Runtime process dispatcher for launching configured tasks and routing generated entities through the QN-MHP model."""

import numpy as np

from basic_BE import See, Hear, Choice, Press_button, Mouse_click, Judge_identity, Judge_relative_location,Count, Cal_single_digit_num,Look_at,Store_to_WM
from gui_general import Tasklist_dic
from utility import attribute_dic
from compound_BE import Look_for, Tracking_1D,Tracking_1D_1W,Tracking_1D_Random,Tracking_2D,Tracking_2D_Random,Tracking_2D_1W,\
    Tracing_1D_Bounded,Tracing_1D_1W,Tracing_2D_Bounded,Tracing_2D_1W


# Explicit registry of supported behavioral elements. Keep names aligned with GUI task definitions.
BE_FUNCTIONS = {
    "See": See,
    "Hear": Hear,
    "Choice": Choice,
    "Press_button": Press_button,
    "Mouse_click": Mouse_click,
    "Judge_identity": Judge_identity,
    "Judge_relative_location": Judge_relative_location,
    "Count": Count,
    "Cal_single_digit_num": Cal_single_digit_num,
    "Look_at": Look_at,
    "Store_to_WM": Store_to_WM,
    "Look_for": Look_for,
    "Tracking_1D": Tracking_1D,
    "Tracking_1D_1W": Tracking_1D_1W,
    "Tracking_1D_Random": Tracking_1D_Random,
    "Tracking_2D": Tracking_2D,
    "Tracking_2D_Random": Tracking_2D_Random,
    "Tracking_2D_1W": Tracking_2D_1W,
    "Tracing_1D_Bounded": Tracing_1D_Bounded,
    "Tracing_1D_1W": Tracing_1D_1W,
    "Tracing_2D_Bounded": Tracing_2D_Bounded,
    "Tracing_2D_1W": Tracing_2D_1W,
}


def get_be_function(name):
    """Resolve a configured behavioral element to its implementation."""
    try:
        return BE_FUNCTIONS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown behavioral element: {name!r}") from exc


entity_info={}
# Sojourn-time and response-time records used by plotting and reporting.

sojourn_time_dic = {}
rt_dic ={1:[],2:[],3:[],4:[],5:[]}
rt_mean_dic={1:[],2:[],3:[],4:[],5:[]}
rt_var_dic={1:[],2:[],3:[],4:[],5:[]}

rmse_dic={}
rmse_var_dic={}
rmse_list=[]



# Dispatch configured behavioral elements through the simulation engine.
def process(qn_mhp,env,i,j,k,attribute,outserver_dic,arrival_time,generation,ppt,cpt,mpt):
            
    j=None
    
    # Record the generated entity attributes.
    entity_info[(i[0],k,generation)]=[]
    if attribute['stimuli']==0:
        entity_info[(i[0],k,generation)].append('noise')
    else:
        for item in attribute.keys() :
            if item=='stimuli' or item=='type' or item=='info':
                entity_info[(i[0],k,generation)].append(attribute_dic[attribute[item]])
            else:
                entity_info[(i[0],k,generation)].append(attribute[item])
    
    # Execute each configured step in task order. 
    step_num=len(Tasklist_dic[k])
    for step in range(step_num):
        if len(Tasklist_dic[k][step])==1:
            a=Tasklist_dic[k][step][0]
            
            yield env.process(get_be_function(a)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
                            
        elif len(Tasklist_dic[k][step])==2:
            a=Tasklist_dic[k][step][0]
            b=Tasklist_dic[k][step][1]
            
            yield env.process(get_be_function(a)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)) & env.process(get_be_function(b)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))

                    
        elif len(Tasklist_dic[k][step])==3:
            a=Tasklist_dic[k][step][0]
            b=Tasklist_dic[k][step][1]
            c=Tasklist_dic[k][step][2]

          
            A=get_be_function(a)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)
            
            B=get_be_function(b)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)                          
   
            C=get_be_function(c)(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)
            yield env.process(A) and env.process(B) and env.process(C)
    

    if attribute['stimuli']!=0:
        sojourn_time_dic[(i[0],k,generation)]='%.2fmsec'%(env.now-arrival_time)
        rt_dic[k].append (env.now - arrival_time)

        rt_mean_dic[k].append(np.mean(rt_dic[k]))
        rt_var_dic[k].append(round(np.std(rt_dic[k]),2))    
    # Look_for may be interrupted when a target is found; it records timing separately.
        

    print('sojourn time for entity%s: %.2fmsec'%((i[0],k,generation),env.now-arrival_time))