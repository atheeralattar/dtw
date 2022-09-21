import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from dtaidistance import dtw

def source_prep(selected_wells, df_raw):
    '''
    This function to prepare the source wells, i.e. the wells that 
    we want to include in our DTW against the target well. Please note that 
    selected_well is the well that is currently drilled
    '''
    import numpy as np
    source_df=df_raw[df_raw.WELL_NAME==selected_well]
    source_df.dropna(how = 'all', axis = 1, inplace=True)
    source_cols = source_df.columns
    return ({'source_df': source_df, 'source_cols': source_cols})

def target_prep(neighbor_wells, df_raw):
    '''
    To prepare the target well, i.e. the well that is currently drilled.
    '''
    target_wells = df_raw[df_raw['WELL_NAME'].isin(neighbor_wells.neighbors)]
    target_wells.dropna(how = 'all', axis = 1, inplace=True)
    return target_wells
    
def dtw1(source_df, target_df, common_columns, neighbor_well):

    '''
    Dynamic Time Warping function, this function will loop through all 
    selected properties to calcluate dtw rank per property pair.
    '''
    
    df_temp = pd.DataFrame(columns = ['feature', 'well', 'distance'])
    common_columns.remove('Depth')
    common_columns.remove('WELL_NAME')
    for col in common_columns:
        distance, path = fastdtw(source_df[col].dropna(how='any', axis=0)/source_df[col].max(),
                                 target_df[col].dropna(how='any', axis=0)/target_df[col].max(), dist=euclidean)
        
        #distance = dtw.distance_fast(source_df[col].to_numpy(), target_df[col].to_numpy())
        df_temp = pd.concat([df_temp, pd.DataFrame({'feature':[col], 'well':[neighbor_well], 'distance':[distance]})])
    
    return df_temp
    

source = source_prep(selected_well, df_raw)
source_df = source['source_df']
source_cols = source['source_cols']
target_df_all = target_prep(neighbor_wells, df_raw)
final_dtw = pd.DataFrame(columns = ['feature', 'well', 'distance'])

for neighbor_well in neighbor_wells['neighbors']:
    print(neighbor_well)
    print('--------------')
    
    
    #Avoiding self DTW
    if neighbor_well == 'Selected Well':
        pass
    else:
        
        target_df= target_df_all[target_df_all.WELL_NAME==neighbor_well]
        target_df.dropna(how='all', axis =1, inplace = True)
        common_columns = list(np.intersect1d(source_cols, target_df.columns))
        print(common_columns)
        #avoiding empty overlaps
        if len(target_df)==0:
            #pass
            temp_dtw =pd.DataFrame({'feature': 'NO DEPTH OVERLAP', 'well': neighbor_well, 'distance': [None]})
            final_dtw = pd.concat([final_dtw, temp_dtw])
        else:
            temp_dtw = dtw1(source_df, target_df, common_columns, neighbor_well)
            final_dtw = pd.concat([final_dtw, temp_dtw])
    final_dtw.reset_index(drop=True, inplace=True)