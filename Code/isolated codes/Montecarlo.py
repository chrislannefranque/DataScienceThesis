import os
import numpy as np
import pandas as pd
import sys
import time
from matplotlib import pyplot as plt
import math
import scipy
from scipy import stats
from tqdm import tqdm
import glaciers_vectors as g

def get_best_distribution(df):
  
  stat=[]
  i = 0

  for distribution in namedistrib1 :  
    b = distribution.fit(df)	# first it is needed to fit the data according to the distribution
    res = scipy.stats.kstest(df,namedistrib2[i],args=b)	# then to evaluate the goodness of the fit according to the Kolmogorov-Smirnov test
    stat.append(res.pvalue)	# pvalue will be the estimator of the goodness of the fit (the higher, the better)
    i = i+1

  stat = np.array(stat)
  #position = np.where(stat == np.nanmax(stat))	# determination of the highest value of pvalue and thus to the best distribution
  #position = np.nanargmax(stat)
  return stat

def sample_glaciers(df,amount):
  
  selection_list = []
  for i in range(1, amount+1): #100
    #draw a random area and random ratio_peri according to the theoretical distribution
    area = scipy.stats.powerlognorm.rvs(*area_td)
    ratio_peri = scipy.stats.weibull_max.rvs(*ratioperi_td)
    
    #get euclidean distance of draw values and all the areas and ratioperi of the glaciers
    df['difference'] = np.sqrt(np.square(df['AREA']-area)+np.square(df['RatioPeri']-ratio_peri))
    
    #get index of glacier with the smallest distance
    selected_index = df['difference'].idxmin() #glacier number x is the closest one to the sample variable
    
    #add index to list
    selection_list.append(selected_index)

    df.drop(selected_index, inplace=True) #remove selected glacier from dataframe
  
  return selection_list

def sample_glaciers2(df, amount:int, glacier_images:dict, images_glaciers:dict):
  
  selection_list = []
  i=0

  while i < amount: 
    #draw a random area and random ratio_peri according to the theoretical distribution
    area = scipy.stats.powerlognorm.rvs(*area_td)
    ratio_peri = scipy.stats.weibull_max.rvs(*ratioperi_td)
    
    #get euclidean distance of draw values and all the areas and ratioperi of the glaciers
    df['difference'] = np.sqrt(np.square(df['AREA']-area)+np.square(df['RatioPeri']-ratio_peri))
    
    #get index of glacier with the smallest distance
    selected_index = df['difference'].idxmin() #glacier number x is the closest one to the sample variable

    #get the asociated main_glacier image
    try:
      selected_image = glacier_images[selected_index+1]

      #add index to list
      selection_list.append(selected_image)
    
      #remove selected glacier and surrounding glaciers from dataframe
      df.drop(df.index[df['Number'].isin(list(images_glaciers[selected_image]))], inplace=True) 

      #increase i by the amount of selected glaciers
      i = i + len(list(images_glaciers[selected_image]))
    
    except:
      pass

  return selection_list


df_ug = pd.read_csv("/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/UG_32619.csv")
df_ug = df_ug[['AREA','RatioPeri','Number']]
#print(df_ug.head())

# different kind of distribution available in Python
namedistrib1 = [scipy.stats.alpha,scipy.stats.anglit,scipy.stats.arcsine,scipy.stats.argus,scipy.stats.beta,scipy.stats.betaprime,scipy.stats.bradford,scipy.stats.burr,scipy.stats.burr12,scipy.stats.cauchy,scipy.stats.chi,scipy.stats.chi2,scipy.stats.cosine,scipy.stats.crystalball,scipy.stats.dgamma,scipy.stats.dweibull,scipy.stats.erlang,scipy.stats.expon,scipy.stats.exponnorm,scipy.stats.exponweib,scipy.stats.exponpow,scipy.stats.f,scipy.stats.fatiguelife,scipy.stats.fisk,scipy.stats.foldcauchy,scipy.stats.foldnorm,scipy.stats.genlogistic,scipy.stats.gennorm,scipy.stats.genpareto,scipy.stats.genexpon,scipy.stats.genextreme,scipy.stats.gausshyper,scipy.stats.gamma,scipy.stats.gengamma,scipy.stats.genhalflogistic,scipy.stats.gilbrat,scipy.stats.gompertz,scipy.stats.gumbel_r,scipy.stats.gumbel_l,scipy.stats.halfcauchy,scipy.stats.halflogistic,scipy.stats.halfnorm,scipy.stats.halfgennorm,scipy.stats.hypsecant,scipy.stats.invgamma,scipy.stats.invgauss,scipy.stats.invweibull,scipy.stats.johnsonsb,scipy.stats.johnsonsu,scipy.stats.kappa4,scipy.stats.kappa3,scipy.stats.ksone,scipy.stats.kstwobign,scipy.stats.laplace,scipy.stats.levy,scipy.stats.levy_l,scipy.stats.logistic,scipy.stats.loggamma,scipy.stats.loglaplace,scipy.stats.lognorm,scipy.stats.lomax,scipy.stats.maxwell,scipy.stats.mielke,scipy.stats.moyal,scipy.stats.nakagami,scipy.stats.ncx2,scipy.stats.ncf,scipy.stats.nct,scipy.stats.norm,scipy.stats.norminvgauss,scipy.stats.pareto,scipy.stats.pearson3,scipy.stats.powerlaw,scipy.stats.powerlognorm,scipy.stats.powernorm,scipy.stats.rdist,scipy.stats.rayleigh,scipy.stats.rice,scipy.stats.recipinvgauss,scipy.stats.semicircular,scipy.stats.skewnorm,scipy.stats.t,scipy.stats.triang,scipy.stats.truncexpon,scipy.stats.truncnorm,scipy.stats.tukeylambda,scipy.stats.uniform,scipy.stats.vonmises,scipy.stats.vonmises_line,scipy.stats.wald,scipy.stats.weibull_min,scipy.stats.weibull_max,scipy.stats.wrapcauchy]

# string related to the different distribution available in Python
namedistrib2 = ['alpha','anglit','arcsine','argus','beta','betaprime','bradford','burr','burr12','cauchy','chi','chi2','cosine','crystalball','dgamma','dweibull','erlang','expon','exponnorm',
'exponweib','exponpow','f','fatiguelife','fisk','foldcauchy','foldnorm','genlogistic','gennorm','genpareto','genexpon','genextreme','gausshyper','gamma','gengamma','genhalflogistic',
'gilbrat','gompertz','gumbel_r','gumbel_l','halfcauchy','halflogistic','halfnorm','halfgennorm','hypsecant','invgamma','invgauss','invweibull','johnsonsb','johnsonsu','kappa4',
'kappa3','ksone','kstwobign','laplace','levy','levy_l','logistic','loggamma','loglaplace','lognorm','lomax','maxwell','mielke','moyal',
'nakagami','ncx2','ncf','nct','norm','norminvgauss','pareto','pearson3','powerlaw','powerlognorm','powernorm','rdist','rayleigh','rice','recipinvgauss','semicircular','skewnorm','t',
'triang','truncexpon','truncnorm','tukeylambda','uniform','vonmises','vonmises_line','wald','weibull_min','weibull_max','wrapcauchy']

stats_area = get_best_distribution(df_ug['AREA'])
area_td = namedistrib1[np.nanargmax(stats_area)].fit(df_ug['AREA'])

stats_rp = get_best_distribution(df_ug['RatioPeri'])
ratioperi_td = namedistrib1[np.nanargmax(stats_rp)].fit(df_ug['RatioPeri'])

#iterative process
df_stats = None
iterations_list = [100,200,500,1000,2000,5000,10000]
for iterations in iterations_list:
  
  best_p_value = 0

  with tqdm(total=iterations) as pbar:
    
    for i in range(1,iterations+1):
      df_aux = df_ug.copy()

      #training_list = sample_glaciers(df_aux, 214)
      training_list = sample_glaciers2(df_aux, 210, g.selected_glaciers_image, g.selected_images)
      training_df = df_ug.iloc[training_list]
      
      #validation_list = sample_glaciers(df_aux, 71)
      validation_list = sample_glaciers2(df_aux, 26, g.selected_glaciers_image, g.selected_images)
      validation_df = df_ug.iloc[validation_list]

      test_df = df_aux[['AREA','RatioPeri','Number']].copy()
      
      area_training_stats = scipy.stats.ks_2samp(df_ug['AREA'],training_df['AREA'])
      rp_training_stats = scipy.stats.ks_2samp(df_ug['RatioPeri'],training_df['RatioPeri'])
      area_validation_stats = scipy.stats.ks_2samp(df_ug['AREA'],validation_df['AREA'])
      rp_validation_stats = scipy.stats.ks_2samp(df_ug['RatioPeri'],validation_df['RatioPeri'])
      area_test_stats = scipy.stats.ks_2samp(df_ug['AREA'],test_df['AREA'])
      rp_test_stats = scipy.stats.ks_2samp(df_ug['RatioPeri'],test_df['RatioPeri'])

      pvalue = area_training_stats[1]*rp_training_stats[1]*area_validation_stats[1]*rp_validation_stats[1]*area_test_stats[1]*rp_test_stats[1]

      #check if pvalue is better
      if pvalue > best_p_value:
        #update the best p value
        best_p_value = pvalue

        #save results in a dictonary
        data = {'Run':i,
                'Max_iterations': iterations,
                'Training': [list(training_df['Number'])],
                'Training_area_pvalue': area_training_stats[1],
                'Training_ratioperi_pvalue': rp_training_stats[1],
                
                'Validation': [list(validation_df['Number'])], 
                'Validation_area_pvalue': area_validation_stats[1],
                'Validation_ratioperi_pvalue': rp_validation_stats[1],
                
                'Test': [list(test_df['Number'])], 
                'Test_area_pvalue': area_test_stats[1],
                'Test_ratioperi_pvalue': rp_test_stats[1],

                'final_pvalue': pvalue
                }
      pbar.update(1)

    try:
      df_stats = df_stats.append(pd.DataFrame(data))
    
    #else we create the dataframe
    except:
      df_stats = pd.DataFrame(data)
        
    #reset index and save the dataframe in pkl
    df_stats.reset_index(drop=True, inplace=True)
    df_stats.to_pickle("/Users/christianlannefranque/Google Drive USM/Thesis_Data/Shapefiles/Cryosphere/UG_32619_fixed_geometry/df_stats_mcm2_"+str(iterations)+".pkl")