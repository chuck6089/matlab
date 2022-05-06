# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 14:30:26 2020
@author: xzd6089
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import datetime
import os



params = {#"fileA_name": "GRR_IQTHT3_03262021.csv", 
          "fileA_name": "GRR_IQTHT3_03262021.csv",  
          "fileB_name": "GRR_IQTHT3_03262021.csv",
          #"fileB_name": "GRR_IQTHT3_03262021.csv", 
          #"fileA_name": "MTF2_GRR_IDolphinwafer_withreference_09032020.csv", 
          #"fileB_name": "MTF2_GRR_IDolphinwafer_withreference_09032020.csv",
    		  "dataPath": "data",
          #"labelB": "IQT-4_csvcontrast_noSLBcalibration",
          #"labelA": "IQTHT1_interpolatedcalculatecontrast_noSLBcalibration",
          "labelA": "1tap_AM",
          "labelB": "4tap_AM",
          "method": "mean",
          #"fileA_filterDict": None, 
#          "fileA_filterDict": {"I": "Green", "F": "N"},
         #"fileB_filterDict": {"E":"Adrian","F":"blue"},
#            "fileA_filterDict": {"B": "30-Dec", "F": "N"},
#            "fileB_filterDict": {"B": "8-Jan", "E": "Y"},
          #"fileA_filterDict": {"F":"IQT4","D":"AE", "G":"Red","E":"Corrected script: 2020-07-28"},
          "fileA_filterDict": {"G":"Blue","C":"Manual","I":"AM"},
          #"fileB_filterDict": {"F":"IQT-HT1","D":"AE", "G":"Blue","E":"08252020_digitalbin_Interpolated Darkfield, calculated contrast"},
          #"fileA_filterDict": {"E":"Alex","F":"blue"},
          "fileB_filterDict": {"G":"Blue","C":"4tap","I":"AM"},
          "fileA_sampleIdCol": ["F"], 
          "fileA_varCol": ["L"],
          "fileB_sampleIdCol" : ["F"], 
          "fileB_varCol": ["L"],         
          "figPath": "figs",
          #"dropSampeId": ['19B251.13.11'],
          "dropSampeId": [''],
           }
    
def ImportSourceFile(*args):    
    fileList = []
    for filename in args:
        filePath = params["dataPath"] + "/" + filename
        if "csv" in filename:
            fileList.append(pd.read_csv(filePath))
        if "xlsx" in filename: 
            fileList.append(pd.read_excel(filePath))
    return fileList

def MakeStringCapital(df):
    cols = [col for col, dt in df.dtypes.items() if dt == object]
    for col in cols:
        df[col] = df[col].map(lambda x: x.upper())
    return df

def ConvertCol2Num(col_str):
    """ Convert base26 column string to number. """
    expn = 0
    col_num = 0
    for char in reversed(col_str):
        col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
        expn += 1
    return col_num

def ConvertCol2Name(df, col_strs):
    '''cols_strs: 
        eg1 : ["A", "b", "cd"]   non-sensitive to capital
        eg2: "A"
        '''
    if type(col_strs)==list:        
        colIxs = [ConvertCol2Num(col_str) - 1 for col_str in col_strs]
        colNames = [df.columns[ix] for ix in colIxs]
    if type(col_strs)==str:
        idIx = ConvertCol2Num(col_strs)-1
        colNames = df.columns[idIx]         
    return colNames

def ApplyFilter(df, filterDict=None):
    '''
    filterDict = {"E": "1200"}
    '''
    colNames = df.columns    
    if type(filterDict)==dict:
        for col in filterDict:
            filterDict[col] = str(filterDict[col])
            val = filterDict[col].upper()
            colIx = ConvertCol2Num(col) - 1
            colName = colNames[colIx] 
            df = df.astype({colName:str})
            if val not in df[colName].unique():
                raise ('ALERT: <{}> DOES NOT EXIST IN COLUMN <{}>'.format(val, colName))
            df = df[df[colName]==val]
    return df
        
def PivotTableMTF(df=None, sampleIdCol=None, cols=None, method=None):
    '''example input: 
        id_col = "A"                      # sample id col
        cols = ["B", "C", "D"]            # cols to be pivoted
        method:  mean, std, min, max, count
    '''
    if not cols:
        raise('NO COLUMN IS GIVEN.')
    if not sampleIdCol:
        raise('SAMPLE ID COLUMN NAME IS NOT GIVEN.')
    colNames = ConvertCol2Name(df, cols)
    idColName = ConvertCol2Name(df, sampleIdCol)
    tb = df[colNames + idColName].groupby(idColName).agg(method)
    return tb
        

def FilterByIndex(df, indexlist):
    return df.loc[df.index.isin(indexlist)]

def FilterByOverlapSampleId(dfs=[None]):   
    df_ix_ls = [set(df.index) for df in dfs]
    sampleIDs = set.intersection(*df_ix_ls)
    return [FilterByIndex(df, sampleIDs) for df in dfs]

def DropSampleId(df, sampleIdList):
    return df.loc[~df.index.isin(sampleIdList)]
	
def PlotFigure(merged,fileAColName,fileBColName, lab1, lab2):
    x,y,sampleIds = merged[lab1].values, merged[lab2].values, merged.index
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    plt.figure(figsize=(10,10))
    plt.style.use('seaborn-poster')
    plt.scatter(x,y,c='r')
    for ix, txt in enumerate(sampleIds):
        plt.annotate(txt, (x[ix]-0.00002,y[ix]+0.00003))
    plt.plot(x, intercept + slope*x, 'y', label="y={:.4f}x+{:.4f} \n\nR2={:.4f} \n\np value={:.6f}\n\nNum_samples = {}".format(slope,intercept,r_value**2,p_value,len(x)))
    #plt.errorbar(x, y,yerr= tb2_std.values, xerr= tb1_std.values, ecolor = "r", fmt='o')
    plt.errorbar(x, y,yerr=merged["std2"], xerr= merged["std1"], ecolor = "r", fmt='o')
    plt.xlabel("{} \n {}".format(lab1, fileAColName))
    plt.ylabel("{} \n {}".format(lab2, fileBColName))
    highlimit = max( max(x) ,max(y) )
    lowlimit = min(min(x) ,min(y) )
    range1 = highlimit - lowlimit
    lowlimit = lowlimit - 0.05*range1
    highlimit = highlimit + 0.05*range1
    plt.ylim(lowlimit,highlimit)
    plt.xlim(lowlimit,highlimit)
    #plt.title("{}".format(params["method"].upper()))
    plt.title("{}".format(params["fileA_filterDict"]["G"]))
    
    if slope < 0:
        plt.plot([highlimit,lowlimit],[lowlimit,highlimit],'k')
        plt.legend(loc=3)
    else:
        plt.plot([lowlimit,highlimit],[lowlimit,highlimit],'k')
        plt.legend(loc=2)
    plt.savefig("{}/{}_{}_{}.jpg".format(params["figPath"],
                                         fileBColName,
                                         params["method"],
                                         str(datetime.date.today()),
                                        ))

def main():
     
    columnnames = ["J","K","L","M","N","O","P","Q","R","S","T","U"];  #Red
    #columnnames = ["J","K","L","M","N","P","Q","S","T"];  #Blue
    #columnnames = ["K","L"];
    #columnnames = ["K","L","M","N","W","X","Y","Z","AE","AF","AK","AL"];
    for colname in columnnames:
        if not os.path.exists(params["figPath"]):
            os.makedirs(params["figPath"])
        [df_A, df_B] = ImportSourceFile(params["fileA_name"],params["fileB_name"] )
        [df_A, df_B] = map(MakeStringCapital,[df_A, df_B])
        df_A_filter = ApplyFilter(df=df_A, filterDict=params["fileA_filterDict"]) 
        df_B_filter = ApplyFilter(df=df_B, filterDict=params["fileB_filterDict"])    
        # get pivot tables
        tb1 = PivotTableMTF(df=df_A_filter,sampleIdCol=params["fileA_sampleIdCol"],cols= [colname], method=params['method'])  #cols=params["fileA_varCol"]
        tb2 = PivotTableMTF(df=df_B_filter,sampleIdCol=params["fileB_sampleIdCol"], cols= [colname], method=params['method'])  #cols=params["fileB_varCol"]
        tb1_std = PivotTableMTF(df=df_A_filter,sampleIdCol=params["fileA_sampleIdCol"],cols= [colname], method="std")    #cols=params["fileA_varCol"]
        tb2_std =  PivotTableMTF(df=df_B_filter,sampleIdCol=params["fileB_sampleIdCol"],cols= [colname], method="std")  #cols=params["fileB_varCol"]
        # keep shared sample ids
        [tb1, tb2, tb1_std, tb2_std] = FilterByOverlapSampleId(dfs=[tb1,tb2, tb1_std, tb2_std])
        fileAColName = ConvertCol2Name(df_A, [colname])[0]   #params["fileA_varCol"]
        fileBColName = ConvertCol2Name(df_B, [colname])[0]  #params["fileB_varCol"]
        lab1, lab2 = params["labelA"], params["labelB"]
        # rename column names
        tb1.columns, tb2.columns = [lab1], [lab2]
        tb1_std.columns = ["std1"]  
        tb2_std.columns = ["std2"] 
        merged = tb1.merge(tb2, left_index=True, right_index=True).sort_values(by=[lab1, lab2])  
        [merged, tb1_std, tb2_std] = [DropSampleId(df, params["dropSampeId"]) for df in [merged, tb1_std, tb2_std]]
        merged = merged.merge(tb1_std, left_index=True, right_index=True)
        merged = merged.merge(tb2_std, left_index=True, right_index=True)
        PlotFigure(merged,fileAColName,fileBColName,lab1,lab2)


if __name__ == "__main__":
    main()