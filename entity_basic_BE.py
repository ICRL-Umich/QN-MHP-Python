# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:55:01 2024

@author: wyuanc
"""
"""Entity-generation functions for basic behavior elements driven by GUI configuration values."""

from random import randint
from utility import color_list, text_list, color_dic
from utility import save_user_input as save
from animation_general import entity_animation
from gui_general import Tasklist_dic,task_info_dic,anim,saved,path
from main_process import process
from utility import random_cpt,random_mpt,random_ppt
import random


j=None
#4.8 entity generation
class entity_generation:
    
    #'eye_loc': [target_x,cursor_x,target_y,cursor_y, target_z,cursor_z]

    def _apply_judge_identity_defaults(self, attribute, k):
        """Populate text/color attributes so Judge_identity uses values consistent with its GUI options."""
        if ['Judge_identity'] not in Tasklist_dic[k]:
            return attribute

        judge_text_options = ['a', 'b', 'c']
        judge_color_options = ['red', 'green', 'blue', 'yellow']

        if 'text' not in attribute or attribute['text'] in ('', None):
            attribute['text'] = judge_text_options[randint(0, len(judge_text_options) - 1)]

        if 'color' not in attribute or attribute['color'] in ('', None, (255,255,255)):
            color_name = judge_color_options[randint(0, len(judge_color_options) - 1)]
            attribute['color'] = color_dic[color_name]

        return attribute
    
    def _apply_count_defaults(self, attribute, k):
        """Attach Count parameters to text entities only."""
        if ['Count'] not in Tasklist_dic[k]:
            return attribute
        from gui_basic_BE import length_count
        if length_count is None:
            raise ValueError('Count Length is missing. Save Count parameters before starting the simulation.')
        count_length = int(length_count)
        if not 1 <= count_length <= 10:
            raise ValueError('Count Length must be an integer between 1 and 10.')
        start = randint(1, 9)
        attribute['Start'] = start
        attribute['End'] = start + count_length - 1
        return attribute

    def color_en (self,env,qn_mhp,k_,fa=None,iat=None,occur=None,**kwargs):
        
        self.color_IAT=iat
        self.color_fa=fa
        self.color_occur=occur
        
      
        generation='color_en'
    
        # initialization
        i = [0]
        index=0
        
        k=eval(k_)
        
        yield env.timeout(self.color_fa)  
        #generate entities
        while True:
            if index<self.color_occur:
                #update entity index i
                index+=1
                i=[index]        
                #update outserver_dic. outserver_dic indicates whether entity can be sent from item server to the next server
                #e.g. if outserver_dic[1] = 1, it means entity can be sent from server1 to server2&3
                #server index in this case: server name 1-8: index1-8 A:101 B:102 C:103 F:104 W:201 Y:202 Z:203
                #server index will be consistent with Hanning's code
                outserver_dic = {}
                for item in range(1,300):
                    outserver_dic[item] = 0
                #update arival time
                arrival_time = env.now
                #update attibute                 
                attribute={'stimuli':1,'type':randint(2,3),'info':randint(4,7),'color':color_list[randint(0, len(color_list)-1)],\
                           'text':'', 'eye_loc':[-999,-999,-999,-999,-999,-999]}
                attribute = self._apply_judge_identity_defaults(attribute, k)
                
                #if only 'SEE' behavior element is chosen, generate visual entities
                if 'seeorhear' in kwargs:
                    if  kwargs['seeorhear']  == 'see':
                        attribute['type']=2
                    else:
                        attribute['type'] =3
                else:
                    
                    if ['See'] in Tasklist_dic[k]:
                        attribute['type']=2
                    if ['Hear'] in Tasklist_dic[k]:
                        attribute['type']=3
                
                
                if any('Choice' in sublist for sublist in Tasklist_dic[k]):   
                    from gui_basic_BE import choice_N
                    N=choice_N[k]
                    if attribute['stimuli']==1:
                        if N==1:
                            attribute['color'] = (255,0,0)  
                        else:
                            attribute['color']=color_list[randint(0, N-1)]
                    
                    
                if any('Look_at' in sublist for sublist in Tasklist_dic[k]):
                    from look_at_target import target_for_task
                    # Preserve stimulus color/text for See -> Choice -> Press_button.
                    # Only the gaze target is changed by Look At.
                    standalone = len(Tasklist_dic[k]) == 1
                    attribute['_visual_gaze_target'] = target_for_task(standalone)
                    attribute['eye_loc'] = attribute['_visual_gaze_target']
                    attribute['type'] = 2
                
                if any('Mouse_click' in sublist for sublist in Tasklist_dic[k]):
                    # Keep the Choice stimulus when Mouse_click follows Choice.
                    # A standalone Mouse_click still uses the original coordinate model.
                    if not any('Choice' in sublist for sublist in Tasklist_dic[k]):
                        attribute = {'stimuli':1, 'type':2, 'info':randint(4,7), 'color':(255,255,255)}
                    attribute['eye_loc'] = [-999,-999,-999,-999,-999,-999]
                    from utility import max_val_click
                    dimension=3
                    for d in range(dimension):
                        target = random.randint(0,max_val_click)
                        attribute['eye_loc'][2*d] = target
                        cursor = random.randint(0,max_val_click)
                        attribute['eye_loc'][2*d+1] = cursor
    
                
                
                attribute = self._apply_judge_identity_defaults(attribute, k)

                attribute = self._apply_judge_identity_defaults(attribute, k)


                i.append(attribute)
    
                if anim==1:             
                    entity_animation().show(i, j, k, '0',generation)
                
                # Call the functions to get a new random process time each entity
                ppt = random_ppt()
                cpt = random_cpt()
                mpt = random_mpt()
                
                env.process(process(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)) 
                #yield env.timeout(expovariate(1/IAT))  # interval arriving time: lamda=1/50 msec           
                yield env.timeout(self.color_IAT)
            else:
                break
    
    
    def text_en (self,env,qn_mhp,k_,fa=None,iat=None,occur=None,**kwargs):
        
        self.text_IAT=iat
        self.text_fa=fa
        self.text_occur=occur
        
        generation='text_en'
    
        # initialization
        i = [0]
        index=0
        
        k=eval(k_)
        
       
        yield env.timeout(self.text_fa)  
        #generate entities
        while True:
            if index<self.text_occur:
                #update entity index i
                index+=1
                i=[index]        
                #update outserver_dic. outserver_dic indicates whether entity can be sent from item server to the next server
                #e.g. if outserver_dic[1] = 1, it means entity can be sent from server1 to server2&3
                #server index in this case: server name 1-8: index1-8 A:101 B:102 C:103 F:104 W:201 Y:202 Z:203
                #server index will be consistent with Hanning's code
                outserver_dic = {}
                for item in range(1,300):
                    outserver_dic[item] = 0
                #update arival time
                arrival_time = env.now
                #update attibute 
                #if only 'SEE' behavior element is chosen, generate visual entities
                attribute={}
                
                attribute = {'stimuli':1,'info':randint(4,7),'color':(255,255,255),'text':'','eye_loc':(-999,-999,-999,-999,-999,-999)}   
                attribute = self._apply_judge_identity_defaults(attribute, k)
        
                
                if ['Cal_single_digit_num'] in Tasklist_dic[k]:
                    attribute={'stimuli':1, 'info':randint(4,7),'color':(255,255,255),'text':''}
                    attribute['cal_sd_num1']=randint(1,9)
                    attribute['cal_sd_num2']=randint(1,9)

                
                if ['Look_at'] in Tasklist_dic[k]:
                    from look_at_target import target_for_task
                    # Preserve stimulus color/text for See -> Choice -> Press_button.
                    # Only the gaze target is changed by Look At.
                    standalone = len(Tasklist_dic[k]) == 1
                    attribute['_visual_gaze_target'] = target_for_task(standalone)
                    attribute['eye_loc'] = attribute['_visual_gaze_target']
                    attribute['type'] = 2

                
                                
                if any('Choice' in sublist for sublist in Tasklist_dic[k]):   
                    if attribute['stimuli']==1:
                        from gui_basic_BE import choice_N
                        N=choice_N[k]
                        if N==1:
                            attribute['text'] = 'A'
                        else:
                            attribute['text']=text_list[randint(0, N-1)]
                
                if any('Mouse_click' in sublist for sublist in Tasklist_dic[k]):
                    # Keep the Choice stimulus when Mouse_click follows Choice.
                    # A standalone Mouse_click still uses the original coordinate model.
                    if not any('Choice' in sublist for sublist in Tasklist_dic[k]):
                        attribute = {'stimuli':1, 'type':2, 'info':randint(4,7), 'color':(255,255,255)}
                    attribute['eye_loc'] = [-999,-999,-999,-999,-999,-999]
                    from utility import max_val_click
                    dimension=3
                    for d in range(dimension):
                        target = random.randint(0,max_val_click)
                        attribute['eye_loc'][2*d] = target
                        cursor = random.randint(0,max_val_click)
                        attribute['eye_loc'][2*d+1] = cursor
                                
                if ['See'] in Tasklist_dic[k]:
                    attribute['type']=2
                if ['Hear'] in Tasklist_dic[k]:
                    attribute['type']=3
                             

                attribute = self._apply_count_defaults(attribute, k)

                i.append(attribute)
                if anim==1:             
                    entity_animation().show(i, j, k, '0',generation)
                
                # Call the functions to get a new random process time each entity
                ppt = random_ppt()
                cpt = random_cpt()
                mpt = random_mpt()
                
                env.process(process(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt)) 
                #yield env.timeout(expovariate(1/IAT))  # interval arriving time: lamda=1/50 msec           
                yield env.timeout(self.text_IAT)
            else:
                break

   