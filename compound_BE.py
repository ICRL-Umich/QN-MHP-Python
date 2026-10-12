# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 08:15:27 2024

@author: wyuanc
"""
"""Compound behavior-element implementations for search, tracking, and tracing tasks."""


from random import randint
from gui_general import anim,SIMTIME
from animation_general import entity_animation
from utility import look_for_ls, n_look_for_ls,color_dic
from utility import real_to_coor_x
from basic_BE import Look_at,See,Judge_identity,Store_to_WM,Judge_relative_location,Choice
import math
import numpy as np

rmse_dic={}
rmse_var_dic={}
rmse_list=[]

def _record_look_for_sojourn(env, entity_id, k, generation, arrival_time):
    from main_process import sojourn_time_dic, rt_dic, rt_mean_dic, rt_var_dic

    sojourn = env.now - arrival_time
    sojourn_time_dic[(entity_id, k, generation)] = '%.2fmsec' % sojourn
    rt_dic[k].append(sojourn)
    rt_mean_dic[k].append(np.mean(rt_dic[k]))
    rt_var_dic[k].append(round(np.std(rt_dic[k]), 2))
    print('sojourn time for entity%s: %.2fmsec' % ((entity_id, k, generation), sojourn))


def Look_for(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, count, generation, ppt, cpt, mpt):

    if count > n_look_for_ls:
        print('Target not found')
        import utility as u
        u.departure_BE_N['Look_for'][k] = i[0]
        _record_look_for_sojourn(env, i[0], k, generation, arrival_time)
        return

    if attribute['stimuli'] == 1:
        yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt))
        yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt))
        yield env.process(Judge_identity(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt))
        yield env.process(Store_to_WM(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt))
        print(count, 'item(s) have already be seen so far')
        from basic_BE import ji_result_dic

        if ji_result_dic[(i[0], k)] == 'F':
            prev_entity_id = i[0]
            prev_arrival_time = arrival_time

            i[0] += 1
            arrival_time = env.now
            attribute = {'stimuli': 1, 'type': 2, 'info': 6}

            if len(look_for_ls) > 1:
                item = randint(1, len(look_for_ls) - 1)
            elif len(look_for_ls) == 1:
                item = 0
            else:
                item = None

            if item is not None:
                attribute['eye_loc'] = look_for_ls[item][0]
                attribute['color'] = look_for_ls[item][2]
                attribute['text'] = look_for_ls[item][1]
            else:
                attribute['eye_loc'] = -999
                attribute['color'] = -999
                attribute['text'] = -999

            i[1] = attribute
            if attribute['color'] != -999:
                i[1]['color'] = color_dic[i[1]['color']]

            if attribute['stimuli'] == 1 and item is not None:
                del look_for_ls[item]
                count += 1

            import utility as u
            u.departure_BE_N['Look_for'][k] = prev_entity_id
            _record_look_for_sojourn(env, prev_entity_id, k, generation, prev_arrival_time)

            if anim == 1:
                entity_animation().show(i, j, k, '0', generation)

            env.process(Look_for(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, count, generation, ppt, cpt, mpt))
            return

        if ji_result_dic[(i[0], k)] == 'T':
            print('entity found', (attribute['eye_loc'], attribute['text'], attribute['color']))
            import utility as u
            u.departure_BE_N['Look_for'][k] = i[0]
            _record_look_for_sojourn(env, i[0], k, generation, arrival_time)
            return
                
from eye_movement_model import set_visual_gaze_target

def Tracking_1D(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #Tracking1D_Bounded
    
    from gui_compound_BE import track1D_b_response
    from display_compound_BE import Reaction_tracking1d_b
    reaction_tracking = Reaction_tracking1d_b(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            print('eye is on cursor: ',(attribute['eye_loc'][1],0))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            print('eye is on target: ',(attribute['eye_loc'][0],0))            
            target = attribute['eye_loc'][0]
            #target location in mm for calculation 
            target_mm = reaction_tracking.mm_coords_target[0]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,1,ppt,cpt,mpt))
           
        
            #Mouse click                      
            if track1D_b_response=='Click mouse':
                from basic_BE import Mouse_click
                
                
                width=reaction_tracking.diameter_mm
                cursor_mm=reaction_tracking.mm_coords_cursor[0]
               
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2)) 
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='1d',width=width,coords=(cursor_mm,target_mm)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target, 0)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                #update cursor location in mm for calculation
                cursor_mm = reaction_tracking.mm_coords_cursor[0]
                
                #update the target location in mm for calculation
                target_new_mm=reaction_tracking.mm_coords_target[0]
                
                #Calculate error                
                square_error=(target_new_mm-cursor_mm)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track1D_b_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                cursor = reaction_tracking.cursor_x
                target = reaction_tracking.target_x
                
                while True:
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor>=target:
                        cursor-=step
                    else:
                        cursor+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor, 0)
                    
                    #update target position
                    target=reaction_tracking.target_x
                    re_count+=1
                    
                    #square error
                    cursor_mm = reaction_tracking.mm_coords_cursor[0]
                    target_mm = reaction_tracking.mm_coords_target[0]
                    square_error=(cursor_mm-target_mm)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()
    
                        
def Tracking_1D_1W(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #entity information
    
    from gui_compound_BE import track1D_1w_response
    from display_compound_BE import Reaction_tracking1d_1w
    reaction_tracking = Reaction_tracking1d_1w(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            print('eye is on cursor: ',(attribute['eye_loc'][1],0))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            print('eye is on target: ',(attribute['eye_loc'][0],0))            
            target = attribute['eye_loc'][0]
            #target location in mm for calculation 
            target_mm = reaction_tracking.mm_coords_target[0]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,1,ppt,cpt,mpt))
           
        
            #Mouse click                      
            if track1D_1w_response=='Click mouse':
                from basic_BE import Mouse_click
                
                
                width=reaction_tracking.diameter_mm
                cursor_mm=reaction_tracking.mm_coords_cursor[0]
               
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2)) 
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='1d',width=width,coords=(cursor_mm,target_mm)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target, 0)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                #update cursor location in mm for calculation
                cursor_mm = reaction_tracking.mm_coords_cursor[0]
                
                #update the target location in mm for calculation
                target_new_mm=reaction_tracking.mm_coords_target[0]
                
                #Calculate error                
                square_error=(target_new_mm-cursor_mm)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track1D_1w_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                cursor = reaction_tracking.cursor_x
                target = reaction_tracking.target_x
                
                while True:
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor>=target:
                        cursor-=step
                    else:
                        cursor+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor, 0)
                    
                    #update target position
                    target=reaction_tracking.target_x
                    re_count+=1
                    
                    #square error
                    cursor_mm = reaction_tracking.mm_coords_cursor[0]
                    target_mm = reaction_tracking.mm_coords_target[0]
                    square_error=(cursor_mm-target_mm)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()



def Tracking_1D_Random(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #entity information
    
    from gui_compound_BE import track1D_r_response
    from display_compound_BE import Reaction_tracking1d_r
    reaction_tracking = Reaction_tracking1d_r(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            print('eye is on cursor: ',(attribute['eye_loc'][1],0))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            print('eye is on target: ',(attribute['eye_loc'][0],0))            
            target = attribute['eye_loc'][0]
            #target location in mm for calculation 
            target_mm = reaction_tracking.mm_coords_target[0]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,1,ppt,cpt,mpt))
           
        
            #Mouse click                      
            if track1D_r_response=='Click mouse':
                from basic_BE import Mouse_click
                
                
                width=reaction_tracking.diameter_mm
                cursor_mm=reaction_tracking.mm_coords_cursor[0]
               
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='1d',width=width,coords=(cursor_mm,target_mm)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target, 0)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                #update cursor location in mm for calculation
                cursor_mm = reaction_tracking.mm_coords_cursor[0]
                
                #update the target location in mm for calculation
                target_new_mm=reaction_tracking.mm_coords_target[0]
                
                #Calculate error                
                square_error=(target_new_mm-cursor_mm)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track1D_r_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                cursor = reaction_tracking.cursor_x
                target = reaction_tracking.target_x
                
                while True:
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 1))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor>=target:
                        cursor-=step
                    else:
                        cursor+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor, 0)
                    
                    #update target position
                    target=reaction_tracking.target_x
                    re_count+=1
                    
                    #square error
                    cursor_mm = reaction_tracking.mm_coords_cursor[0]
                    target_mm = reaction_tracking.mm_coords_target[0]
                    square_error=(cursor_mm-target_mm)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()
    
def Tracking_2D(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #Tracking_2D_Bounded
    from gui_compound_BE import track2D_b_response
    from display_compound_BE import Reaction_tracking2d_b
    reaction_tracking = Reaction_tracking2d_b(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2+\
            (reaction_tracking.mm_coords_cursor[1]-reaction_tracking.mm_coords_target[1])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            attribute['eye_loc'][3] = reaction_tracking.cursor_y
            print('eye is on cursor: ',(attribute['eye_loc'][1],attribute['eye_loc'][3]))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            attribute['eye_loc'][2] = reaction_tracking.target_y
            print('eye is on target: ',(attribute['eye_loc'][0],attribute['eye_loc'][2]))            
            target_x = attribute['eye_loc'][0]
            target_y = attribute['eye_loc'][2]
            #target location in mm for calculation 
            target_mm_x = reaction_tracking.mm_coords_target[0]
            target_mm_y = reaction_tracking.mm_coords_target[1]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,2,ppt,cpt,mpt))
           
            #Mouse click                      
            if track2D_b_response=='Click mouse':
                from basic_BE import Mouse_click
   
                width=reaction_tracking.diameter_mm
                cursor_mm_x=reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y=reaction_tracking.mm_coords_cursor[1]
                
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 8))
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='2d',width=width,coords=(cursor_mm_x,target_mm_x,cursor_mm_y,target_mm_y)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target_x, target_y)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                attribute['eye_loc'][3]=reaction_tracking.cursor_y
                #update cursor location in mm for calculation
                cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                
                #update the target location in mm for calculation
                target_new_mm_x=reaction_tracking.mm_coords_target[0]
                target_new_mm_y=reaction_tracking.mm_coords_target[1]
                
                #Calculate error                
                square_error=(target_new_mm_x-cursor_mm_x)**2+(target_new_mm_y-cursor_mm_y)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track2D_b_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                while True:
                    
                    #update target and cursor position:
                    cursor_x = reaction_tracking.cursor_x
                    target_x = reaction_tracking.target_x
                    
                    #move along x axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_x>=target_x:
                        cursor_x-=step
                    else:
                        cursor_x+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, reaction_tracking.cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                    
                    #update target and position:
                    cursor_y = reaction_tracking.cursor_y   
                    target_y = reaction_tracking.target_y
                    
                    #move along y axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_y>=target_y:
                        cursor_y-=step
                    else:
                        cursor_y+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()
    

def Tracking_2D_Random(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #entity information
    
    from gui_compound_BE import track2D_r_response,track2D_r_amp,track2D_r_freq
    from display_compound_BE import Reaction_tracking2d_r
    from utility import track2D_amp_dic,track2D_freq_dic
    reaction_tracking = Reaction_tracking2d_r(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2+\
            (reaction_tracking.mm_coords_cursor[1]-reaction_tracking.mm_coords_target[1])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            attribute['eye_loc'][3] = reaction_tracking.cursor_y
            print('eye is on cursor: ',(attribute['eye_loc'][1],attribute['eye_loc'][3]))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            attribute['eye_loc'][2] = reaction_tracking.target_y
            print('eye is on target: ',(attribute['eye_loc'][0],attribute['eye_loc'][2]))            
            target_x = attribute['eye_loc'][0]
            target_y = attribute['eye_loc'][2]
            #target location in mm for calculation 
            target_mm_x = reaction_tracking.mm_coords_target[0]
            target_mm_y = reaction_tracking.mm_coords_target[1]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,2,ppt,cpt,mpt))
           
        
            #Mouse click                      
            if track2D_r_response=='Click mouse':
                from basic_BE import Mouse_click
                
                
                width=reaction_tracking.diameter_mm
                cursor_mm_x=reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y=reaction_tracking.mm_coords_cursor[1]
                
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 8))
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='2d',width=width,coords=(cursor_mm_x,target_mm_x,cursor_mm_y,target_mm_y)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target_x, target_y)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                attribute['eye_loc'][3]=reaction_tracking.cursor_y
                #update cursor location in mm for calculation
                cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                
                #update the target location in mm for calculation
                target_new_mm_x=reaction_tracking.mm_coords_target[0]
                target_new_mm_y=reaction_tracking.mm_coords_target[1]
                
                #Calculate error                
                square_error=(target_new_mm_x-cursor_mm_x)**2+(target_new_mm_y-cursor_mm_y)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track2D_r_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                while True:
                    
                    #update target and position:
                    cursor_x = reaction_tracking.cursor_x
                    target_x = reaction_tracking.target_x
                    
                    #move along x axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_x>=target_x:
                        cursor_x-=step
                    else:
                        cursor_x+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, reaction_tracking.cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                    
                    #update target and position:
                    cursor_y = reaction_tracking.cursor_y   
                    target_y = reaction_tracking.target_y
                    
                    #move along y axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_y>=target_y:
                        cursor_y-=step
                    else:
                        cursor_y+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()

def Tracking_2D_1W(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    #Tracking_2D_Bounded
    from gui_compound_BE import track2D_1w_response
    from display_compound_BE import Reaction_tracking2d_1w
    reaction_tracking = Reaction_tracking2d_1w(environment = env)
    reaction_tracking.plot_curve()
    
    start_time=env.now
    if attribute['stimuli']==1:
        re_count=0
        #calculate the square error at the start
        square_error=(reaction_tracking.mm_coords_cursor[0] - reaction_tracking.mm_coords_target[0])**2+\
            (reaction_tracking.mm_coords_cursor[1]-reaction_tracking.mm_coords_target[1])**2
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
        while env.now<SIMTIME:
            #Look at and see for cursor        
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.cursor_x, getattr(reaction_tracking, "cursor_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][1] = reaction_tracking.cursor_x
            attribute['eye_loc'][3] = reaction_tracking.cursor_y
            print('eye is on cursor: ',(attribute['eye_loc'][1],attribute['eye_loc'][3]))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Look at and see for target
            set_visual_gaze_target(attribute, reaction_tracking, reaction_tracking.target_x, getattr(reaction_tracking, "target_y", None))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))   
            #update target location, which is also the location that mouse should click at
            attribute['eye_loc'][0] = reaction_tracking.target_x
            attribute['eye_loc'][2] = reaction_tracking.target_y
            print('eye is on target: ',(attribute['eye_loc'][0],attribute['eye_loc'][2]))            
            target_x = attribute['eye_loc'][0]
            target_y = attribute['eye_loc'][2]
            #target location in mm for calculation 
            target_mm_x = reaction_tracking.mm_coords_target[0]
            target_mm_y = reaction_tracking.mm_coords_target[1]
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
            
            #Judge relative location
            yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,2,ppt,cpt,mpt))
           
            #Mouse click                      
            if track2D_1w_response=='Click mouse':
                from basic_BE import Mouse_click
   
                width=reaction_tracking.diameter_mm
                cursor_mm_x=reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y=reaction_tracking.mm_coords_cursor[1]
               
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 8))
                yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                              dimension='2d',width=width,coords=(cursor_mm_x,target_mm_x,cursor_mm_y,target_mm_y)))
                
                #show cursor after clicking 
                reaction_tracking.move_point_to(target_x, target_y)
                #update cursor position
                attribute['eye_loc'][1]=reaction_tracking.cursor_x
                attribute['eye_loc'][3]=reaction_tracking.cursor_y
                #update cursor location in mm for calculation
                cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                
                #update the target location in mm for calculation
                target_new_mm_x=reaction_tracking.mm_coords_target[0]
                target_new_mm_y=reaction_tracking.mm_coords_target[1]
                
                #Calculate error                
                square_error=(target_new_mm_x-cursor_mm_x)**2+(target_new_mm_y-cursor_mm_y)**2
                
                re_count+=1
                
                #Calculate RMSE
                rmse_list.append(square_error)
                rmse_dic[re_count] = (np.sum(rmse_list)/(re_count+1))**(1/2)
                rmse_var_dic[re_count]=np.std(rmse_list)
                            
            elif track2D_1w_response=='Press keyboard':
                
                from basic_BE import Press_button
                
                step=1 #in coordinate 1-100
                
                while True:
                    
                    #update target and cursor position:
                    cursor_x = reaction_tracking.cursor_x
                    target_x = reaction_tracking.target_x
                    
                    #move along x axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_x>=target_x:
                        cursor_x-=step
                    else:
                        cursor_x+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, reaction_tracking.cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                    
                    #update target and position:
                    cursor_y = reaction_tracking.cursor_y   
                    target_y = reaction_tracking.target_y
                    
                    #move along y axis
                    yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
                    yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
                    
                    #update cursor postion:
                    if cursor_y>=target_y:
                        cursor_y-=step
                    else:
                        cursor_y+=step
                    #show cursor
                    reaction_tracking.move_point_to(cursor_x, cursor_y)
                    
                    re_count+=1
                    
                    #square error
                    cursor_mm_x = reaction_tracking.mm_coords_cursor[0]
                    cursor_mm_y = reaction_tracking.mm_coords_cursor[1]
                    target_mm_x = reaction_tracking.mm_coords_target[0]
                    target_mm_y = reaction_tracking.mm_coords_target[1]
                    square_error=(cursor_mm_x-target_mm_x)**2+(cursor_mm_y-target_mm_y)**2
                    #calculate RMSE
                    rmse_list.append(square_error)
                    rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
                    rmse_var_dic[re_count]=np.std(rmse_list)
                        
    reaction_tracking.root.mainloop()

def Tracing_1D_Bounded(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    
    from utility import tracing1D_amp_dic
    from gui_compound_BE import tracing1D_b_direc,tracing1D_b_amp,tracing1D_b_response
    print(tracing1D_b_response)
    from basic_BE import Press_button, Mouse_click
    from display_compound_BE import Reaction_tracing1d_b
    reaction_tracing = Reaction_tracing1d_b()

    # Plot the curve
    reaction_tracing.plot_curve()
    moving_direction = tracing1D_b_direc 
    if moving_direction=='forward':
        reaction_tracing.moving_forward = True
    else:
        reaction_tracing.moving_forward = False
    re_count = 0 
    #look at and see the point position 
    set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.current_x, getattr(reaction_tracing, "current_y", None))
    yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
    attribute['eye_loc'][1] = reaction_tracing.current_x
    print('eye is on the point: ',(reaction_tracing.current_x,reaction_tracing.current_y))
    yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
    
    
    while env.now <= SIMTIME:
        
        #check if the point changes moving direction, if changes, look at and see the end of the curve, otherwise pass
        #the initial value of reaction_tracing.reach is 1, so the first look at and see of the end would be the initial one before start the moving  
        if reaction_tracing.reach == 1:
            #look at and see the end of the curve 
            set_visual_gaze_target(attribute, reaction_tracing, (reaction_tracing.end_x if reaction_tracing.moving_forward else 0), None)
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            #which end:
            if reaction_tracing.moving_forward:
                attribute['eye_loc'][0] = reaction_tracing.end_x
                print('eye is on end: ',(reaction_tracing.end_x,reaction_tracing.end_y))
            else:
                attribute['eye_loc'][0] = 0
                print('eye is on end: ',(0,reaction_tracing.start_y))
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
        #update current point position
        attribute['eye_loc'][1] = reaction_tracing.current_x
        
        #assuming judge magnitude and press button on horizontal direction first, and then vertical direction 
        #movement along x axis
        yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,1,ppt,cpt,mpt))
        
        if tracing1D_b_response == 'Press keyboard':
            #Choice BE for button (L or R)
            yield env.process (Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
            yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))  
            #show point x movement on reaction window
            reaction_tracing.move_point(magnitude_x = tracing1D_amp_dic[tracing1D_b_amp],magnitude_y=0)
        
        elif tracing1D_b_response == 'Click mouse':
            magnitude_click = 10
            width = reaction_tracing.diameter_mm
            cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
            click_mm= reaction_tracing.click_location_mm(reaction_tracing.current_x, 0, magnitude_click, 0)
            click_mm_x = click_mm[0]
            #click mouse: choose from 2 directions: left right
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N=2))
            yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                          dimension='1d',width=width,coords=(cursor_mm_x,click_mm_x,0,0)))
        
            reaction_tracing.move_point(magnitude_click, 0)
        
        re_count+=1
        cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
        if reaction_tracing.moving_forward:
            square_error=(cursor_mm_x-reaction_tracing.mm_x_end)**2
        else:
            square_error=(cursor_mm_x-reaction_tracing.mm_x_start)**2 
        #calculate RMSE
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
        rmse_var_dic[re_count]=np.std(rmse_list)
        
    reaction_tracing.root.mainloop()


def Tracing_1D_1W(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    
    from utility import tracing1D_amp_dic
    from gui_compound_BE import tracing1D_1w_amp,tracing1D_1w_response
    from basic_BE import Press_button,Mouse_click
    from display_compound_BE import Reaction_tracing1d_1w
    reaction_tracing = Reaction_tracing1d_1w()

    # Plot the curve
    reaction_tracing.plot_curve()
    
    re_count = 0
    #look at and see the point position 
    set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.current_x, getattr(reaction_tracing, "current_y", None))
    yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
    attribute['eye_loc'][1] = reaction_tracing.current_x
    print('eye is on the point: ',(reaction_tracing.current_x,reaction_tracing.current_y))
    yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
    
    while env.now <= SIMTIME:
        #check if the current screen changes
        if reaction_tracing.new_screen == 1:
            #look at and see the end of the curve in the current screen 
            set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.x_max, None)
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][0] = reaction_tracing.x_max
            print('eye is on end: ',(reaction_tracing.x_max,reaction_tracing.y_end))

            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
 
        #assuming judge magnitude and press button on horizontal direction first, and then vertical direction 
        #movement along x axis
        yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,1,ppt,cpt,mpt))
        
        if tracing1D_1w_response == 'Press keyboard':
            #Choice BE for button (L or R)
            yield env.process (Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
            yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))  
            #show point x movement on reaction window
            reaction_tracing.move_point(magnitude_x = tracing1D_amp_dic[tracing1D_1w_amp],magnitude_y=0)
        
        elif tracing1D_1w_response == 'Click mouse':
            magnitude_click = 10
            width = reaction_tracing.diameter_mm
            cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
            click_mm= reaction_tracing.click_location_mm(reaction_tracing.current_x, 0, magnitude_click, 0)
            click_mm_x = click_mm[0]
            #click mouse: choose from 2 directions: left right
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N=2))
            yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, \
                                          dimension='1d',width=width,coords=(cursor_mm_x,click_mm_x,0,0)))
        
            reaction_tracing.move_point(magnitude_click, 0)
        
        re_count+=1
        cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
        square_error=(cursor_mm_x-reaction_tracing.mm_x_end)**2
        #calculate RMSE
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
        rmse_var_dic[re_count]=np.std(rmse_list)
            
        
    
    reaction_tracing.root.mainloop()

def Tracing_2D_Bounded(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    
    from utility import tracing2D_amp_x_dic,tracing2D_amp_y_dic
    from gui_compound_BE import tracing2D_b_direc,tracing2D_b_x_amp,tracing2D_b_y_amp,tracing2D_b_response
    from basic_BE import Press_button, Mouse_click
    from display_compound_BE import Reaction_tracing2d_b
    reaction_tracing = Reaction_tracing2d_b()

    # Plot the curve
    reaction_tracing.plot_curve()
    moving_direction = tracing2D_b_direc 
    if moving_direction=='forward':
        reaction_tracing.moving_forward = True
    else:
        reaction_tracing.moving_forward = False
    re_count = 0
    #look at and see the point position 
    set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.current_x, getattr(reaction_tracing, "current_y", None))
    yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
    attribute['eye_loc'][2] = reaction_tracing.current_x
    attribute['eye_loc'][3] = reaction_tracing.current_y
    print('eye is on the point: ',(reaction_tracing.current_x,reaction_tracing.current_y))
    yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
    
    
    while env.now <= SIMTIME:
        #check if the point changes moving direction, if changes, look at and see the end of the curve, otherwise pass
        
        if reaction_tracing.reach ==1:
            #look at and see the end of the curve 
            set_visual_gaze_target(attribute, reaction_tracing, (reaction_tracing.end_x if reaction_tracing.moving_forward else 0), (reaction_tracing.end_y if reaction_tracing.moving_forward else reaction_tracing.start_y))
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            #which end:
            if reaction_tracing.moving_forward:
                attribute['eye_loc'][0] = reaction_tracing.end_x
                attribute['eye_loc'][1] = reaction_tracing.end_y
                print('eye is on end: ',(reaction_tracing.end_x,reaction_tracing.end_y))
            else:
                attribute['eye_loc'][0] = 0
                attribute['eye_loc'][1] = reaction_tracing.start_y
                print('eye is on end: ',(0,reaction_tracing.start_y))
            
            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))    
        #assuming judge magnitude and press button on horizontal direction first, and then vertical direction 
        #movement along x axis
        yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,2,ppt,cpt,mpt))
        
        if tracing2D_b_response == 'Press keyboard':
            #Choice BE for button (L or R)
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
            yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))  
            #show point x movement on reaction window
            reaction_tracing.move_point(magnitude_x = tracing2D_amp_x_dic[tracing2D_b_x_amp],magnitude_y=0)
            #Choice BE for button (U or D)
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
            yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))   
            #show point y movement on reaction window
            reaction_tracing.move_point(0,magnitude_y = tracing2D_amp_y_dic[tracing2D_b_y_amp])
        
        elif tracing2D_b_response == 'Click mouse':
            magnitude_click_x = tracing2D_amp_x_dic[tracing2D_b_x_amp]
            magnitude_click_y =  tracing2D_amp_y_dic[tracing2D_b_y_amp]
            width = reaction_tracing.diameter_mm
            cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
            cursor_mm_y = reaction_tracing.mm_coords_cursor[1]
            click_mm= reaction_tracing.click_location_mm(reaction_tracing.current_x, reaction_tracing.current_y, \
                                                         magnitude_click_x, magnitude_click_y)
            click_mm_x = click_mm[0]
            click_mm_y = click_mm[1]
            #click mouse: choose from 8 directions: left right up down upright upleft downright downleft
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N=8))
            yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt,\
                                          dimension='2d',width=width,coords=(cursor_mm_x,click_mm_x,cursor_mm_y,click_mm_y)))
            reaction_tracing.move_point(magnitude_click_x, magnitude_click_y)

        re_count+=1
        cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
        cursor_mm_y = reaction_tracing.mm_coords_cursor[1]
        if reaction_tracing.moving_forward:
            square_error=(cursor_mm_x-reaction_tracing.mm_x_end)**2+(cursor_mm_y-reaction_tracing.mm_y_end)**2
        else:
            square_error=(cursor_mm_x-reaction_tracing.mm_x_start)**2+(cursor_mm_y-reaction_tracing.mm_y_start)**2 
        #calculate RMSE
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
        rmse_var_dic[re_count]=np.std(rmse_list)
    reaction_tracing.root.mainloop()
    
def Tracing_2D_1W(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt):
    # Use a separate gaze target; legacy eye_loc still supports cursor/target logic.
    attribute.pop('_legacy_tracking_eye', None)
    
    from utility import tracing2D_amp_x_dic,tracing2D_amp_y_dic
    from gui_compound_BE import tracing2D_1w_x_amp,tracing2D_1w_y_amp,tracing2D_1w_response
    from basic_BE import Press_button, Mouse_click
    from display_compound_BE import Reaction_tracing2d_1w
    reaction_tracing = Reaction_tracing2d_1w()

    # Plot the curve
    reaction_tracing.plot_curve()
    re_count = 0
    #look at and see the point position 
    set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.current_x, getattr(reaction_tracing, "current_y", None))
    yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
    attribute['eye_loc'][2] = reaction_tracing.current_x
    attribute['eye_loc'][3] = reaction_tracing.current_y
    print('eye is on the point: ',(reaction_tracing.current_x,reaction_tracing.current_y))
    yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
    
    
    while env.now <= SIMTIME:
        #check if the current screen changes
        if reaction_tracing.new_screen == 1:
            #look at and see the end of the curve in the current screen 
            set_visual_gaze_target(attribute, reaction_tracing, reaction_tracing.x_max, reaction_tracing.y_end)
            yield env.process(Look_at(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time,generation,ppt,cpt,mpt))
            attribute['eye_loc'][0] = reaction_tracing.x_max
            attribute['eye_loc'][1] = reaction_tracing.y_end
            print('eye is on end: ',(reaction_tracing.x_max,reaction_tracing.y_end))

            yield env.process(See(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))
 
        #assuming judge magnitude and press button on horizontal direction first, and then vertical direction 
        #movement along x axis
        yield env.process(Judge_relative_location(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,2,ppt,cpt,mpt))
        
        if tracing2D_1w_response == 'Press keyboard':
            #Choice BE for button (L or R)
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))
            yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt))  
            #show point x movement on reaction window
            reaction_tracing.move_point(magnitude_x = tracing2D_amp_x_dic[tracing2D_1w_x_amp],magnitude_y=0)
            #Choice BE for button (U or D)
            if reaction_tracing.press_y:
                yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N = 2))  
                yield env.process(Press_button(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation,ppt,cpt,mpt)) 
                #show point y movement on reaction window
                reaction_tracing.move_point(0,magnitude_y = tracing2D_amp_y_dic[tracing2D_1w_y_amp])
        elif tracing2D_1w_response == 'Click mouse':
            magnitude_click_x = tracing2D_amp_x_dic[tracing2D_1w_x_amp]
            magnitude_click_y =  tracing2D_amp_y_dic[tracing2D_1w_y_amp]
            width = reaction_tracing.diameter_mm
            cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
            cursor_mm_y = reaction_tracing.mm_coords_cursor[1]
            click_mm= reaction_tracing.click_location_mm(reaction_tracing.current_x, reaction_tracing.current_y, \
                                                         magnitude_click_x, magnitude_click_y)
            click_mm_x = click_mm[0]
            click_mm_y = click_mm[1]
            #click mouse: choose from 8 directions: left right up down upright upleft downright downleft
            yield env.process(Choice(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt, choice_N=8))
            yield env.process(Mouse_click(qn_mhp, env, i, j, k, attribute, outserver_dic, arrival_time, generation, ppt, cpt, mpt,\
                                          dimension='2d',width=width,coords=(cursor_mm_x,click_mm_x,cursor_mm_y,click_mm_y)))
            reaction_tracing.move_point(magnitude_click_x, magnitude_click_y)

        re_count+=1
        cursor_mm_x = reaction_tracing.mm_coords_cursor[0]
        cursor_mm_y = reaction_tracing.mm_coords_cursor[1]
        square_error=(cursor_mm_x-reaction_tracing.mm_x_end)**2+(cursor_mm_y-reaction_tracing.mm_y_end)**2
        #calculate RMSE
        rmse_list.append(square_error)
        rmse_dic[re_count] = (np.sum(rmse_list))**(1/2)/(re_count+1)
        rmse_var_dic[re_count]=np.std(rmse_list)
            

    
    reaction_tracing.root.mainloop()
    
    
    
    
    
    
    
    
    
    
    
    