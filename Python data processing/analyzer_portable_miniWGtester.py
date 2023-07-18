# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 13:57:15 2023

Data analyzer for portable miniWG tester

@author: xzd6089
"""

import os
import numpy as np
import cv2
from matplotlib import pyplot
import glob
import pandas as pd
import csv

class portable_analyzer():
    def __init__(self,path = None, debug = False) -> None:
        self.debug = debug
        if path: 
            self.path = path
            if os.path.isdir(path):
                os.chdir(path)
    def load_SLB(self, slbcheckerpath,slbnegcheckerpath, slbclearpath):
        self.slbchecker = cv2.imread(slbcheckerpath,cv2.IMREAD_GRAYSCALE)
        self.slbnegchecker = cv2.imread(slbnegcheckerpath,cv2.IMREAD_GRAYSCALE)
        self.slbclear = cv2.imread(slbclearpath,cv2.IMREAD_GRAYSCALE)
            
    def load_dark(self,darkpath):
        #darkimagenames = glob.glob("*.bmp")
        self.darkimage = cv2.imread(darkpath,cv2.IMREAD_GRAYSCALE)
        self.width = self.darkimage.shape[1]
        self.height = self.darkimage.shape[0]
        
    def load_checker_negchecker(self,checkerpath, negcheckerpath):
        self.checker = cv2.imread(checkerpath,cv2.IMREAD_GRAYSCALE)
        self.negchecker = cv2.imread(negcheckerpath,cv2.IMREAD_GRAYSCALE)
        
    def load_ghost(self,ghostpath):
        self.ghost = cv2.imread(ghostpath, cv2.IMREAD_GRAYSCALE)
        self.displayghost = obj.ghost.copy()
        
    def meancontrast(self,checker_m,checker_n,squaresize_m = 127, squaresize_n = 127,ROI_portion = 0.6,center_m = None,center_n = None):    #checker_m is number of columns, #checker_n is number of rows
        if center_m == None:
            center_m = self.width/2
        if center_n == None:
            center_n = self.height/2
        
        #center_m = self.width - center_m
        #center_n = self.height - center_n
        ROIsize_m = round(squaresize_m * ROI_portion)
        ROIsize_n = round(squaresize_n * ROI_portion)
        ROIcenters = [[[0]*2 for i in range(checker_m)] for j in range(checker_n)]   #j is index of rows, j is index of columns
        self.meancontrast = 0
        self.hmeancontrast = 0
        self.contrastcsv =  [[[-1] for i in range(checker_m)] for j in range(checker_n)]  
        self.Contrastmap =  [[[0]*3 for i in range(checker_m)] for j in range(checker_n)]   # order is checker brigthness, negchecker brightness and contrast for ROI of each checker
        for i in range(checker_m):
            for j in range(checker_n):
                ROIcenters[j][i] = [j * squaresize_n + center_n - (checker_n-1)*squaresize_n/2, i * squaresize_m + center_m - (checker_m-1)*squaresize_m/2] 
                self.Contrastmap[j][i][0] = np.mean(self.checker[int(ROIcenters[j][i][0] - round(ROIsize_n/2))-1: int(ROIcenters[j][i][0] + round(ROIsize_n/2)) +1 , int(ROIcenters[j][i][1]-round(ROIsize_m/2)) -1 : int(ROIcenters[j][i][1] + round(ROIsize_m/2)) + 1 ])     #calculate the mean brigthenss for this checker
                self.Contrastmap[j][i][1] = np.mean(self.negchecker[int(ROIcenters[j][i][0] - round(ROIsize_n/2))-1: int(ROIcenters[j][i][0] + round(ROIsize_n/2)) +1 , int(ROIcenters[j][i][1]-round(ROIsize_m/2)) -1 : int(ROIcenters[j][i][1] + round(ROIsize_m/2)) + 1 ])
                if  self.Contrastmap[j][i][0] >  self.Contrastmap[j][i][1]:
                    self.contrastcsv[j][i]  = self.Contrastmap[j][i][2] =  self.Contrastmap[j][i][0]/ self.Contrastmap[j][i][1]                    
                else:
                    self.Contrastmap[j][i][2] =  self.Contrastmap[j][i][1]/ self.Contrastmap[j][i][0]
                    self.contrastcsv[j][i] = self.Contrastmap[j][i][1]/ self.Contrastmap[j][i][0]
                self.meancontrast = self.meancontrast + self.Contrastmap[j][i][2]
                self.hmeancontrast = self.hmeancontrast + 1.0/self.Contrastmap[j][i][2]
                cv2.rectangle(self.checker, (int(ROIcenters[j][i][1]-round(ROIsize_m/2)),int(ROIcenters[j][i][0] - round(ROIsize_n/2))),  (int(ROIcenters[j][i][1] + round(ROIsize_m/2)),int(ROIcenters[j][i][0] + round(ROIsize_n/2))) , (255, 255, 255), 2)
        self.meancontrast = self.meancontrast/(checker_m * checker_n)
        self.hmeancontrast = checker_m * checker_n/self.hmeancontrast          

        # Need to add SLB checker and negcheck contrast map and calibrate the DUT checker and negchecker to SLB checker contrast

    def SLB_contrast(self,checker_m,checker_n,squaresize_m = 127, squaresize_n = 127,ROI_portion = 0.6,center_m = None,center_n = None):    #checker_m is number of columns, #checker_n is number of rows
        if center_m == None:
            center_m = self.width/2
        if center_n == None:
            center_n = self.height/2
        
        #center_m = self.width - center_m
        #center_n = self.height - center_n
        ROIsize_m = round(squaresize_m * ROI_portion)
        ROIsize_n = round(squaresize_n * ROI_portion)
        ROIcenters = [[[0]*2 for i in range(checker_m)] for j in range(checker_n)]   #j is index of rows, j is index of columns
        self.slb_meancontrast = 0
        self.slb_hmeancontrast = 0
        self.slb_contrastcsv =  [[[-1] for i in range(checker_m)] for j in range(checker_n)]  
        self.SLBContrastmap =  [[[0]*3 for i in range(checker_m)] for j in range(checker_n)]   # order is checker brigthness, negchecker brightness and contrast for ROI of each checker
        for i in range(checker_m):
            for j in range(checker_n):
                ROIcenters[j][i] = [j * squaresize_n + center_n - (checker_n-1)*squaresize_n/2, i * squaresize_m + center_m - (checker_m-1)*squaresize_m/2] 
                self.SLBContrastmap[j][i][0] = np.mean(self.slbchecker[int(ROIcenters[j][i][0] - round(ROIsize_n/2))-1: int(ROIcenters[j][i][0] + round(ROIsize_n/2)) +1 , int(ROIcenters[j][i][1]-round(ROIsize_m/2)) -1 : int(ROIcenters[j][i][1] + round(ROIsize_m/2)) + 1 ])     #calculate the mean brigthenss for this checker
                self.SLBContrastmap[j][i][1] = np.mean(self.slbnegchecker[int(ROIcenters[j][i][0] - round(ROIsize_n/2))-1: int(ROIcenters[j][i][0] + round(ROIsize_n/2)) +1 , int(ROIcenters[j][i][1]-round(ROIsize_m/2)) -1 : int(ROIcenters[j][i][1] + round(ROIsize_m/2)) + 1 ])
                if  self.SLBContrastmap[j][i][0] >  self.SLBContrastmap[j][i][1]:
                    self.slb_contrastcsv[j][i]  = self.SLBContrastmap[j][i][2] =  self.SLBContrastmap[j][i][0]/ self.SLBContrastmap[j][i][1]                    
                else:
                    self.SLBContrastmap[j][i][2] =  self.SLBContrastmap[j][i][1]/ self.SLBContrastmap[j][i][0]
                    self.slb_contrastcsv[j][i] = self.SLBContrastmap[j][i][1]/ self.SLBContrastmap[j][i][0]
                self.slb_meancontrast = self.slb_meancontrast + self.SLBContrastmap[j][i][2]
                self.slb_hmeancontrast = self.slb_hmeancontrast + 1.0/self.SLBContrastmap[j][i][2]
                cv2.rectangle(self.slbchecker, (int(ROIcenters[j][i][1]-round(ROIsize_m/2)),int(ROIcenters[j][i][0] - round(ROIsize_n/2))),  (int(ROIcenters[j][i][1] + round(ROIsize_m/2)),int(ROIcenters[j][i][0] + round(ROIsize_n/2))) , (255, 255, 255), 2)
        self.slb_meancontrast = self.slb_meancontrast/(checker_m * checker_n)
        self.slb_hmeancontrast = checker_m * checker_n/self.slb_hmeancontrast  
    
    def contrastcalibration(self):
        checker_n = len(obj.contrastcsv)
        checker_m = len(obj.contrastcsv[0])
        self.calibrated_contrastcsv =  [[[-1] for i in range(checker_m)] for j in range(checker_n)]
        self.calibrated_meancontrast = 0
        self.calibrated_hmeancontrast = 0
        for idx, e in np.ndenumerate(self.contrastcsv):
            self.calibrated_contrastcsv[idx[0]][idx[1]] = 1.0/(1.0/self.contrastcsv[idx[0]][idx[1]] - 1.0/self.slb_contrastcsv[idx[0]][idx[1]])
            self.calibrated_meancontrast = self.calibrated_meancontrast + self.calibrated_contrastcsv[idx[0]][idx[1]]
            self.calibrated_hmeancontrast = self.calibrated_hmeancontrast + 1.0/self.calibrated_contrastcsv[idx[0]][idx[1]]
        self.calibrated_meancontrast = self.calibrated_meancontrast/(checker_m * checker_n)
        self.calibrated_hmeancontrast = checker_m * checker_n/self.calibrated_hmeancontrast
        
        
    
    
    def Ghost(self):  #repeated chosen ROI for ghost and original image
        [H,W] = self.ghost.shape
        self.points = [(-1,-1)]*4
        
        #ghostflag = False
        self.n = 0   
        self.ghostdata = pd.DataFrame(columns=["source_x","source_y","ghost_x","ghost_y", "source_brightness", "ghost_brigthness","ghost_strength"])
        
        self.Windowname = "first pick topleft corner then pick bottom right corner, must be in order, click any key to quit"
        
        cv2.namedWindow(self.Windowname,cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow(self.Windowname,self.displayghost)
        cv2.setMouseCallback(self.Windowname, self.draw_rectangle)
        
        # while True:
        #     cv2.imshow("Ghost picking, click q to quit",displayghost)
        #     key = cv2.waitKey(1) & 0xFF        
            
            
        #     if key == ord('q') or key == 27:
        #         break
        
        cv2.waitKey(0)        
        cv2.destroyAllWindows()
        #cv2.imwrite('Ghost.png',self.displayghost)
        
            
        
    def draw_rectangle(self,event, x, y, flags, param):
        global ghostflag, top_left_clicked, bottom_right_clicked
        
        #print((x,y))
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.n % 4 == 0:   #topleft corner of source image
                self.points[0] = (x,y)
                cv2.circle(self.displayghost, self.points[0], radius= 2, color=(255, 255, 255), thickness= -1)
            if self.n% 4 == 1: 
                self.points[1] = (x,y)
                cv2.rectangle(self.displayghost, self.points[0], self.points[1], (120,120,120), 2)
                cv2.putText(self.displayghost, "Source# {:d}".format(self.n//4 + 1), self.points[1], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            if self.n% 4 == 2: 
                self.points[2] = (x,y)
                cv2.circle(self.displayghost, self.points[2], radius= 2, color=(255, 255, 255), thickness= -1)
            if self.n% 4 == 3: 
                self.points[3] = (x,y) 
                cv2.rectangle(self.displayghost, self.points[2], self.points[3], (255,255,255), 2)
                ghostbrightness = np.mean(self.ghost[self.points[2][1]:self.points[3][1],self.points[2][0]:self.points[3][0]])
                sourcebrightness = np.mean(self.ghost[self.points[0][1]:self.points[1][1],self.points[0][0]:self.points[1][0]])
                #self.ghostdata.append(pd.DataFrame([self.points[0][0],self.points[0][1],self.points[1][0],self.points[1][1],sourcebrightness,ghostbrightness,ghostbrightness/sourcebrightness]),ignore_index=True) 
                rowtoappend = {"source_x":self.points[0][0]
                               ,"source_y":self.points[0][1]
                                   ,"ghost_x":self.points[1][0]
                                       ,"ghost_y":self.points[1][1]
                                           ,"source_brightness":sourcebrightness
                                               ,"ghost_brigthness":ghostbrightness
                                                   ,"ghost_strength":ghostbrightness/sourcebrightness}
                
                self.ghostdata = self.ghostdata.append(rowtoappend, ignore_index=True)
                cv2.putText(self.displayghost, "Ghost# {:d},strengh: {:.4f}".format(self.n//4 + 1,ghostbrightness/sourcebrightness), self.points[3], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)                
                
            print("point {:d}: ({:d}, {:d})".format(self.n%4 + 1,x,y))
            #cv2.putText(self.displayghost, "What", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.imshow(self.Windowname,self.displayghost)
            self.n = self.n + 1
        
     #def store_data(self):

def save_to_csv(data, file_name, mode = 'w'):
    with open(file_name, mode, newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(data)
         

if __name__ == "__main__":
    folderpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708'
    darkpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\DarkField\20230708200717010_0.bmp'
    checkerpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\20230708192640701_0.bmp'
    negcheckerpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\20230708192650843_0.bmp'
    slbcheckerpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\Baseline\20230708220725306_0.bmp'
    slbnegcheckerpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\Baseline\20230708220720963_0.bmp'
    slbclearpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\Baseline\20230708220716516_0.bmp'
    Ghostpath = r'G:\Shared drives\Display & Optics Drive - Archive\Waveguide\Waveguide Metrology\Portable WGtester\data\20230708\Test1_Sample1A_DefaultCameraSettings\20230708192702672_0.bmp'
    
    obj = portable_analyzer(folderpath)
    obj.load_dark(darkpath)
    obj.load_checker_negchecker(checkerpath,negcheckerpath)
    obj.load_ghost(Ghostpath)
    obj.load_SLB(slbcheckerpath, slbnegcheckerpath, slbclearpath)
    #darkfield subtraction
    obj.checker = obj.checker - obj.darkimage
    obj.negchecker = obj.negchecker - obj.darkimage
    obj.ghost = obj.ghost - obj.darkimage
    obj.SLB_contrast(10, 8, squaresize_m = 127, squaresize_n = 127,  center_m = 2315, center_n = 1495)
    obj.meancontrast(10, 8, squaresize_m = 127, squaresize_n = 127,  center_m = 2199, center_n = 1800)
    obj.contrastcalibration()
    
    print("SLB Checkerboard mean contrast is {:.5f}".format(obj.slb_meancontrast))
    print("SLB Checkerboard harmonic mean contrast is {:.5f}".format(obj.slb_hmeancontrast))
    print("Ucalibrated Checkerboard mean contrast is {:.5f}".format(obj.meancontrast))
    print("Ucalibrated Checkerboard harmonic mean contrast is {:.5f}".format(obj.hmeancontrast))
    print("Calibrated Checkerboard mean contrast is {:.5f}".format(obj.calibrated_meancontrast))
    print("Calibrated Checkerboard harmonic mean contrast is {:.5f}".format(obj.calibrated_hmeancontrast))
    
    
    cv2.namedWindow("SLB_checkerimage",cv2.WINDOW_NORMAL)
    cv2.imshow("SLB_checkerimage",obj.slbchecker)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('SLB_checker.png',obj.checker)
    
    cv2.namedWindow("checkerimage",cv2.WINDOW_NORMAL)
    cv2.imshow("checkerimage",obj.checker)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('checker.png',obj.checker)
    
    #Measure ghost
    obj.Ghost()
    cv2.imwrite('Ghost.png',obj.displayghost)
    obj.ghostdata.to_csv('Ghostdata.csv')
    save_to_csv(obj.slb_contrastcsv, "SLB_contrastmap.csv", mode = 'w')
    save_to_csv(obj.contrastcsv, "Ucalibrated_contrastmap.csv", mode = 'w')
    save_to_csv(obj.calibrated_contrastcsv, "Calibrated_contrastmap.csv", mode = 'w')
    
    meandata = [
        ["Mean contrast",obj.meancontrast],
        ["Harmonic mean contrast",obj.hmeancontrast]
        ]
    save_to_csv(meandata, "Ucalibrated_contrastmap.csv", mode = 'a')
    
    slbmeandata = [
        ["SLB_Meancontrast",obj.slb_meancontrast],
        ["SLB_Harmonic mean contrast",obj.slb_hmeancontrast]
        ]
    save_to_csv(slbmeandata, "SLB_contrastmap.csv", mode = 'a')
    
    calibrated_meandata = [
        ["SLB_Meancontrast",obj.calibrated_meancontrast],
        ["SLB_Harmonic mean contrast",obj.calibrated_hmeancontrast]
        ]
    save_to_csv(calibrated_meandata, "Calibrated_contrastmap.csv", mode = 'a')
    
    
