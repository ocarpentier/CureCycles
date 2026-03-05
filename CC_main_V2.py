import numpy as np


##Functions
def Det_AB(time, T_lead, T_min, T_max):
    maskA = T_lead > T_min
    maskB = T_lead > T_max
    if np.any(maskA):
        indexA = np.argmax(maskA)
        T_A =  T_lead[indexA]
        t_A = time[indexA]
    else:
        raise(Exception(f'There is no temperature higher than {T_min}'))
    
    if np.any(maskB):
        indexB = np.argmax(maskB)
        T_B = T_lead[indexB]
        t_B = time[indexB]
    else:
        raise(Exception(f'There is no temperature higher than {T_max}'))
    
    return T_A, T_B, t_A, t_B


def Det_CD(time, T_lag, T_min, T_max):
    maskC = T_lag > T_min
    maskD = T_lag > T_max

    if np.any(maskC):
        indexC = np.argmax(maskC)
        T_C = T_lag[indexC]
        t_C = time[indexC]
    else:
        raise(Exception(f'There is no temperature higher than {T_min}'))

    if np.any(maskD):
        indexD = np.argmax(maskD)
        T_D = T_lag[indexD]
        t_D = time[indexD]
    else:
        raise(Exception(f'There is no temperature higher than {T_max}'))
    
    return T_C, T_D, t_C, t_D


def Det_KL(time, T_lead, T_lag,T_lower):
    maskK = T_lead < T_lower
    maskL = T_lag < T_lower
    if np.any(maskK):
        indexK = np.argmax(maskK)
        T_K =  T_lead[indexK]
        t_K = time[indexK]
    else:
        raise(Exception(f'There is no temperature higher than {T_min}')) #TODO solve impossibel reference
    
    if np.any(maskL):
        indexL = np.argmax(maskL)
        T_L = T_lag[indexL]
        t_L = time[indexL]
    else:
        raise(Exception(f'There is no temperature higher than {T_max}'))  #TODO solve impossibel reference
    
    return T_K, T_L, t_K, t_L


def Det_Js(time, T_lead, T_lag, T_air, T_lower):
    maskJ = T_air < T_lower
    maskJ1 = T_lead < T_lower
    maskJ2 = T_lag < T_lower

    if np.any(maskJ):
        indexJ = np.argmax(maskJ)
        T_J, T_J3, T_J4 = T_air[indexJ], T_lead[indexJ], T_lag[indexJ]
        t_J, t_J3, t_J4 = time[indexJ], time[indexJ], time[indexJ]
        
    else:
        raise(Exception(f'After this dwell the airtemp does not lower anymore'))

    if np.any(maskJ1):
        indexJ1 = np.argmax(maskJ1)
        T_J1 = T_lead[indexJ1]
        t_J1 = time[indexJ1]
    else:
        raise(Exception(f'After this dwell the leading does not lower anymore'))

    if np.any(maskJ2):
        indexJ2 = np.argmax(maskJ2)
        T_J2 = T_lag[indexJ2]
        t_J2 = time[indexJ2]
    else:
        raise(Exception(f'After this dwell the lagging does not lower anymore'))
    
    return T_J, T_J1, T_J2, T_J3, T_J4, t_J, t_J1, t_J2, t_J3, t_J4

def find_first_exceeding_index_with_threshold(arr, mask, duration):
    # Use a sliding window to check if the value exceeds the threshold for the specified duration
    for i in range(int(len(arr) - duration + 1)):
        if np.all(mask[i:int(i + duration)]):
            return i
    return None


def Det_Es(time, T_lead, T_lag, T_air, T_upper, Unit_csv='min',duration=30):
    
    maskE = T_air > T_upper
    maskE1 = T_lead > T_upper
    maskE2 = T_lag > T_upper

    
    if np.any(maskE):
        if Unit_csv == 'min':
            duration = 30/(time[1]-time[0])
        else:
            duration = 30*60/(time[1]-time[0])
        
        indexE = find_first_exceeding_index_with_threshold(T_air, maskE,duration=duration)
        T_E = T_air[indexE]
        t_E = time[indexE]
    else:
        raise(Exception(f'After this dwell the airtemp does not rise anymore'))
    if np.any(maskE1):
        indexE1 = np.argmax(maskE1)
        T_E1 = T_lead[indexE1]
        t_E1 = time[indexE1]
    else:
        raise(Exception(f'After this dwell the leading does not rise anymore'))

    if np.any(maskE2):
        indexE2 = np.argmax(maskE2)
        T_E2 = T_lag[indexE2]
        t_E2 = time[indexE2]
    else:
        raise(Exception(f'After this dwell the lagging does not rise anymore'))
    
    return T_E, T_E1, T_E2, t_E, t_E1, t_E2

def get_start_to_end_cure(T_start_cond,T_end_cond,T_lag,T_lead,time,Unit_csv):
    # define temp of start condition
    T_start, T_end = T_start_cond[0], T_end_cond[0]

    # Find the index of the first and last value of the cure
    maskT = T_lag >= T_start
    index_init = np.argmax(maskT)
    
    maskT = T_lag >= T_end
    index_last = len(maskT) - 1 - np.argmax(maskT[::-1])
    
    if time[index_init]<=T_start_cond[1] and Unit_csv=='min' and T_start_cond[1] != -1:
        maskt = time >= T_start_cond[1]
        index_init = np.argmax(maskt)
    
    elif time[index_init]/60<=T_start_cond[1] and Unit_csv=='sec'  and T_start_cond[1] != -1:
        maskt = time >= T_start_cond[1]*60
        index_init = np.argmax(maskt)

    return index_init,index_last


def Check_cycles(time, T_lead, T_lag, T_air, phases_lst, T_start_cond, T_end_cond, DT_lst, Dt_lst,Heatup_rate_lst, Cooldownrate = None, Unit_csv='min'):
    check_lst = []
    log_lst = []
    # define temp of start condition
    T_start, T_end = T_start_cond[0], T_end_cond[0]
    # Find the index of the value
    maskT = T_lead > T_start_cond[0]
    index_init = np.argmax(maskT)
    
    # define max and min cooldownrate
    if Cooldownrate is not None:
        Cooldownmax = Cooldownrate[1]
        if Cooldownrate[0]==-1:
            Cooldownmin = None
        else:
            Cooldownmin = Cooldownrate[0]

    phases = ['heatup','dwell','cure','cooldown'] #possible phases during curing, The curing phaase is seen as dwell.
    init = True #Boolean to check whether it the start or just another
    T_A, T_B = None, None
    t_A, t_B = None, None
    index_heatup = 0
    index_dwell = 0

    index_cycle = 0 # From which index to start counting for the further cycles

    for idx, phase in enumerate(phases_lst):
        
        if phase == phases[0] and init:
            Heat_up_rate = Heatup_rate_lst[index_heatup]

            T_A, T_B, t_A, t_B = Det_AB(time, T_lead, T_start, DT_lst[0][0])
            T_C, T_D, t_C, t_D = Det_CD(time, T_lag,T_start, DT_lst[0][0])
            init = False
            
            # get the index of the lates temerature take into account
            t_max = max((t_A, t_B, t_C, t_D))
            maskt = time >= t_max
            if np.any(maskt):
                index_cycle = np.argmax(maskt)

            #If csv is in seconds, change to minutes
            if Unit_csv.lower() == 'sec':
                t_A, t_B, t_C, t_D =  t_A/60, t_B/60, t_C/60, t_D/60 
            
            
            max_rate = (T_B-T_A)/(t_B-t_A)
            min_rate = (T_D-T_C)/(t_D-t_C)

            #store if the heatup rate was good and the actual values
            if max_rate>max(Heat_up_rate):
                check_lst.append([1,f'Heat up rate in step {index_heatup+1} is too high! (= {round(max_rate,3)} [deg/min])'])
            elif min_rate<min(Heat_up_rate):
                check_lst.append([1,f'Heat up rate in step {index_heatup+1} is too low! (= {round(min_rate,3)} [deg/min])'])
            else:
                check_lst.append([0,f'Max rate = {round(max_rate,3)} [deg/min] \nMin rate = {round(min_rate,3)} [deg/min]'])
            
            index_heatup += 1

        elif phase == phases[0]:
            Heat_up_rate = Heatup_rate_lst[index_heatup]

            T_A, T_B, t_A, t_B = Det_AB(time, T_lead, DT_lst[index_heatup-1][1], DT_lst[index_heatup][0])
            T_C, T_D, t_C, t_D = Det_CD(time, T_lag, DT_lst[index_heatup-1][1], DT_lst[index_heatup][0])
            
            # get the index of the lates temerature take into account
            t_max = max((t_A, t_B, t_C, t_D))
            maskt = time >= t_max
            if np.any(maskt):
                index_cycle = np.argmax(maskt)

            #If csv is in seconds, change to minutes
            if Unit_csv.lower() == 'sec':
                t_A, t_B, t_C, t_D =  t_A/60, t_B/60, t_C/60, t_D/60 
            
            
            max_rate = (T_B-T_A)/(t_B-t_A)
            min_rate = (T_D-T_C)/(t_D-t_C)

            #store if the heatup rate was good and the actual values
            if max_rate>max(Heat_up_rate):
                check_lst.append([1,f'Heat up rate in step {index_heatup+1} is too high! (= {round(max_rate,3)} [deg/min])'])
            elif min_rate<min(Heat_up_rate):
                check_lst.append([1,f'Heat up rate in step {index_heatup+1} is too low! (= {round(min_rate,3)} [deg/min])'])
            else:
                check_lst.append([0,f'Max heat up rate = {round(max_rate,3)} [deg/min] \nheat up rate = {round(min_rate,3)} [deg/min]'])
            
            index_heatup += 1

        elif phase == phases[1]:
            
            T_E, T_E1, T_E2, t_E, t_E1, t_E2 = Det_Es(time, T_lead, T_lag, T_air, DT_lst[index_dwell][1],Unit_csv=Unit_csv,duration=Dt_lst[-1][0])
            
        
            # get the index of the lates temerature take into account
            t_max = max((t_E, t_E1, t_E2))
            maskt = time >= t_max
            if np.any(maskt):
                index_cycle = np.argmax(maskt)

            #If csv is in seconds, change to minutes
            if Unit_csv.lower() == 'sec':
                t_E, t_E1, t_E2 =  t_E/60, t_E1/60, t_E2/60
            
            dwell_time_lead = t_E-t_B
            dwell_time_lag = t_E - t_D
            dwell_time_max = max((dwell_time_lag,dwell_time_lead))
            dwell_time_min = min((dwell_time_lag,dwell_time_lead))

            if dwell_time_max>Dt_lst[index_dwell][1]:
                check_lst.append([1,f'Dwell time has been exceeded with {round(dwell_time_max,3)} [min]'])
            elif dwell_time_min<Dt_lst[index_dwell][0]:
                check_lst.append([1,f'Dwell time has been too short with {round(dwell_time_min,3)} [min]'])
            else:
                check_lst.append([0,f'Dwell time is max:{round(dwell_time_max,3)} and min: {round(dwell_time_min,3)} [min]'])

            index_dwell += 1

        elif phase == phases[2]:
            
            T_J, T_J1, T_J2, T_J3, T_J4, t_J, t_J1, t_J2, t_J3, t_J4 = Det_Js(time[index_cycle::], T_lead[index_cycle::], T_lag[index_cycle::], T_air[index_cycle::], T_lower=DT_lst[index_dwell][0])
            
            # get the index of the first temerature take into account
            t_max = min((t_J, t_J1, t_J2, t_J3, t_J4))
            maskt = time <= t_max
            if np.any(maskt):
                index_cycle = np.argmin(maskt) # This is used by the Js determination in cooldown phase

            #If csv is in seconds, change to minutes
            if Unit_csv.lower() == 'sec':
                t_J, t_J1, t_J2, t_J3, t_J4 =  t_J/60, t_J1/60, t_J2/60, t_J3/60, t_J4/60
            
            if Cooldownrate==None:
                dwell_time_lead = t_J1-t_B
                dwell_time_lag = t_J2 - t_D
            else:
                dwell_time_lead = t_J-t_B
                dwell_time_lag = t_J - t_D

            dwell_time_max = max((dwell_time_lag,dwell_time_lead))
            dwell_time_min = min((dwell_time_lag,dwell_time_lead))

            if dwell_time_max>Dt_lst[index_dwell][1]:
                check_lst.append([1,f'Cure time has been exceeded, taking {round(dwell_time_max,3)} [min]'])
            elif dwell_time_min<Dt_lst[index_dwell][0]:
                check_lst.append([1,f'Cure time has been too short, taking only {round(dwell_time_min,3)} [min]'])
            else:
                check_lst.append([0,f'Cure time is max:{round(dwell_time_max,3)} and min: {round(dwell_time_min,3)} [min]'])

            #chekc if any temperature exceeds th upper limit.
            if np.any(T_lead>DT_lst[index_dwell][1]):
                check_lst.append([1,f'The temperature exceeds a certain threshold.'])

            index_dwell += 1

        elif phase == phases[3] and Cooldownrate is not None:
            
            T_J, T_J1, T_J2, T_J3, T_J4, t_J, t_J1, t_J2, t_J3, t_J4 = Det_Js(time[index_cycle::], T_lag[index_cycle::], T_lead[index_cycle::], T_air[index_cycle::], T_lower=DT_lst[index_dwell-1][0])
            T_K, T_L, t_K, t_L = Det_KL(time[index_cycle::], T_lag[index_cycle::], T_lead[index_cycle::], T_end) 


            #If csv is in seconds, change to minutes
            if Unit_csv.lower() == 'sec':
                t_J, t_J1, t_J2, t_J3, t_J4, t_K, t_L =  t_J/60, t_J1/60, t_J2/60, t_J3/60, t_J4/60, t_K/60, t_L/60

            if Cooldownrate==None:
                max_cooldown = (T_J1-T_K)/(t_J1-t_K)
            else:
                max_cooldown = (T_J3-T_K)/(t_J3-t_K)

            if Cooldownrate==None:
                min_cooldown = (T_J2-T_L)/(t_J2-t_L)
            else:
                min_cooldown = (T_J4-T_L)/(t_J4-t_L)
            
            #store if its good or not
            if abs(max_cooldown)>abs(Cooldownmax):
                check_lst.append([1,f'The maximum cooldownrate has been exceeded with {round(max_cooldown,2)}'])

            if Cooldownmin is not None:
                if abs(min_cooldown)<abs(Cooldownmin):
                    check_lst.append([1,f'The minimum cooldownrate has been exceeded with {round(min_cooldown,2)}'])
            else:
                check_lst.append([0,f'Maximum cooldown rate is {round(max_cooldown,2)} \nMinimum cooldown rate is {round(min_cooldown,2)}'])

    return check_lst



def Check_Pressure(time, Press, AP, T_lag, T_lead, T_start_cond, T_end_cond, Unit_csv='min'):
    check_lst = []
    
    index_init, index_last =get_start_to_end_cure(T_start_cond,T_end_cond,T_lag,T_lead,time,Unit_csv)
    
    if np.any(Press>AP[1]):
        indices = np.argwhere(Press>AP[1])        
        for index_highP in indices:
            if index_highP > index_init and index_highP<index_last:
                if Unit_csv == 'min':
                    check_lst.append([1,f'Pressure is too high at time = {round(time[index_highP][0],2)} [min]'])
                else:
                    check_lst.append([1,f'Pressure is too high at time = {round(time[index_highP][0]/60,2)} [min]'])

    if np.any(Press<AP[0]):
        indices = np.argwhere(Press<AP[0])        
        for index_lowP in indices:
            if index_lowP > index_init and index_lowP<index_last:
                if Unit_csv == 'min':
                    check_lst.append([1,f'Pressure is too low at time = {round(time[index_lowP][0],2)} [min]'])
                else:
                    check_lst.append([1,f'Pressure is too low at time = {round(time[index_lowP][0]/60,2)} [min]'])

    if not (np.any(Press<AP[0]) and np.any(Press>AP[1])):
        check_lst.append([0,f'Autoclave pressure is good'])

    return check_lst


def Check_Vacuum(time, Vacuum,Presssure_drive, vac_range, T_lag, T_lead, T_start_cond, T_end_cond, Unit_csv='sec'):
    check_lst = []

    index_init, index_last =get_start_to_end_cure(T_start_cond,T_end_cond,T_lag,T_lead, time,Unit_csv)
        
    maskP = Presssure_drive>0

    true_indices = np.where(maskP)[0]
    first_true = true_indices[0]
    last_true = true_indices[-1]
    

    if np.any(Vacuum>vac_range[1]):

        indices = np.argwhere(Vacuum>vac_range[1])
        # Print the indices
        for index_highP in indices:
            if index_highP > index_init and index_highP<index_last and not (index_highP>=first_true and index_highP <= last_true+6): # the "+6" allows for the leaktest to settle for 1 minute
                
                if Unit_csv == 'min':
                    check_lst.append([1, f'Vacuum is too high at time = {round(time[index_highP][0],2)}, with pressure = {round(Vacuum[index_highP][0],2)} kPa\n'])
                    
                else:
                    check_lst.append([1,f'Vacuum is too high at time = {round(time[index_highP][0]/60,2)}, with pressure = {round(Vacuum[index_highP][0],2)} kPa\n'])

    
    if np.any(Vacuum<vac_range[0]):
        
        indices = np.argwhere(Vacuum<vac_range[0])
        # Print the indices
        for index_lowP in indices:
            if index_lowP > index_init and index_lowP<index_last and not (index_lowP>first_true and index_lowP < last_true+6): # the "+6" allows for the leaktest to settle for 1 minute
            
                if Unit_csv == 'min':
                    check_lst.append([1,f'Vacuum is too low at time = {round(time[index_lowP][0],2)}'])
                else:
                    check_lst.append([1,f'Vacuum is too low at time = {round(time[index_lowP][0]/60,2)}'])
    if check_lst == []:
        return [[0,f'Vacuum was withing bounds.']]
    else:
        return check_lst
    

def check_leaktest(time, Pressure_meas, Presssure_drive, Thresh_leaktest):
    check_lst = []

    maskP = Presssure_drive>0
    true_indices = np.where(maskP)[0]
    first_true = true_indices[0]
    last_true = true_indices[-1]

    diffP = Pressure_meas[last_true]-Pressure_meas[first_true]
    if diffP>Thresh_leaktest:
        check_lst.append([1, f'The pressure difference is too large: delta_P={round(diffP,3)} kPa at time={round(time[last_true]/60)}.'])
        
    else:
        check_lst.append([0,f'The delta P during leaktest={round(diffP,3)} kPa'])
    
    return check_lst[0]


def spread(T_lag, T_lead,time,Threshold=16):
    check_lst = []

    spread_arr = np.abs(T_lead-T_lag)
    # Find indices where values exceed the threshold
    indices = np.argwhere(spread_arr > Threshold)
    # Print the indices
    for idx in indices:
        check_lst.append([1,f'The spread is too high at {time[idx]} with {spread_arr[idx]} [deg C]'])

    if check_lst == []:
        return [0,f'Spread was within bounds with max spread: {round(max(spread_arr),3)} [deg C]']
    else:
        return check_lst
    
