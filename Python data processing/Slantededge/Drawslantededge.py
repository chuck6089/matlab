# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 10:41:03 2020

Generating predistorted reticle pattern for slanted edge MTF for WG IQT 

@author: Zhida Xu
"""

import svgwrite
import math
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF 
from reportlab.graphics.shapes import Drawing
from svgwrite import cm,mm
from common1 import splitfn
from xlrd import open_workbook
import pandas as pd
from scipy.interpolate import griddata


#Draw the final image on the camera sensor plane

Res_H = 6576;  Res_V = 4384; 
camerapixelsize = 5.5   #unit in um
cameraEFL = 21.55286372  #unit in mm

Squaresize = 200 #Size of rectangle 
Slant_angle = -5 #slant angle in degs
slant_radian = math.radians(Slant_angle); #slant angle in radians
centercoor = [Res_H/2 , Res_V/2 ];  #center coordinate in X/Y coordinate
Squarelength = Squaresize * camerapixelsize / 1000;  #square length in mm
Squarediag = Squaresize * camerapixelsize *2* np.sin(math.radians(45)) /1000; #square diagnol length in mm

Fiducialcoordup = [[0,0],[Squarelength*np.cos(slant_radian),Squarelength*np.sin(slant_radian)],[Squarediag*np.cos(np.pi/4 +slant_radian),Squarediag*np.sin(np.pi/4 + slant_radian)],[Squarelength*np.cos(np.pi/2 + slant_radian),Squarelength*np.sin(np.pi/2 +slant_radian)]];
Fiducialcoorddwon = [[0,0],[Squarelength*np.cos(np.pi + slant_radian),Squarelength*np.sin(np.pi + slant_radian)],[Squarediag*np.cos(np.pi*5/4 +slant_radian),Squarediag*np.sin(np.pi*5/4 + slant_radian)],[Squarelength*np.cos(np.pi*3/2 + slant_radian),Squarelength*np.sin(np.pi*3/2 +slant_radian)]];
 
#Field angle to plot in degrees
fovs =  - 200 * np.ones((12,2));
fovs[0] = [0,0]
fovs[1] = [20,0]
fovs[2] = [-20,0]
fovs[3] = [0,10]
fovs[4] = [0,-10]

fiducialcenters = [];

Dist_camera = pd.read_csv('C:/Users/XZD6089/Dropbox (Facebook)/Python data processing/Slantededge/87degFOVlens_distortion_522nm.txt',
                 encoding='utf-16',
                 sep='\t')

XYFieldangle = np.array(Dist_camera.iloc[:,[2,3]]); #YFieldangle = Dist_camera.iloc[:,3]; 
RealX = Dist_camera.iloc[:,7]; RealY = Dist_camera.iloc[:,8]; 

nsquares = 0;
for fov in fovs:
    if fov[0] < -80 or fov[1] < -80:
        break;
    else:
#        centerX.append(float(griddata(XYFieldangle, RealX, (fov),  method='linear'))); 
#        centerY.append(float(griddata(XYFieldangle, RealY, (fov),  method='linear'))); 
        fiducialcenters.append([float(griddata(XYFieldangle, RealX, (fov),  method='linear')),float(griddata(XYFieldangle, RealY, (fov),  method='linear'))])
        nsquares = nsquares + 1;

fiducialcenters = np.array(fiducialcenters);

Fiducialups = [];
Fiducialdowns = [];

for fiducial in fiducialcenters:    #Calculate the coordinate of corners of 2 fiducials 
    fiducialup = Fiducialcoordup + fiducial; 
    Fiducialups.append(fiducialup);
    fiducialdown = Fiducialcoorddwon + fiducial;
    Fiducialdowns.append(fiducialdown);

#convert to pixel coordinate
Fiducialdownspix = np.array(Fiducialdowns)*1000/camerapixelsize;
Fiducialupspix = np.array(Fiducialups)*1000/camerapixelsize;

Fiducialdownspix = Fiducialdownspix + centercoor;
Fiducialupspix = Fiducialupspix + centercoor;

nfiducial = len(Fiducialups);
#Generate the svg graph
dwg = svgwrite.Drawing(filename = 'imageplane_slantededge.svg', size = (Res_H, Res_V))
#dwg.viewbox(width= Res_H, height= Res_V);

dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='black'))

for i in range(nfiducial): 
    fidup = dwg.polygon(points=[(Fiducialdownspix[i,0,0],Fiducialdownspix[i,0,1]),(Fiducialdownspix[i,1,0],Fiducialdownspix[i,1,1]),(Fiducialdownspix[i,2,0],Fiducialdownspix[i,2,1]),(Fiducialdownspix[i,3,0],Fiducialdownspix[i,3,1])], fill='white')
    fidown = dwg.polygon(points=[(Fiducialupspix[i,0,0],Fiducialupspix[i,0,1]),(Fiducialupspix[i,1,0],Fiducialupspix[i,1,1]),(Fiducialupspix[i,2,0],Fiducialupspix[i,2,1]),(Fiducialupspix[i,3,0],Fiducialupspix[i,3,1])], fill='white')
    dwg.add(fidup)
    dwg.add(fidown)
dwg.save()    


######## Start the tracing from camera image plane to reticle plane

res_print = 5; # in um

xres = 3000; yres  = 3000;  #resolution of generated reticles

centercoor2 = [xres/2 , yres/2];

Dist_camera2reticle = pd.read_csv('C:/Users/XZD6089/Dropbox (Facebook)/Python data processing/Slantededge/Distortion_camera2reticle_9degcant_Green.txt',
                 encoding='utf-16',
                 sep='\t')

XYFieldheight = np.array(Dist_camera2reticle.iloc[:,[2,3]]);
RealX2 = np.array(Dist_camera2reticle.iloc[:,7]); RealY2 = np.array(Dist_camera2reticle.iloc[:,8]); 

Reticlefidup = np.array(Fiducialups); 
Reticlefidown = np.array(Fiducialdowns);

Fiducialups = np.array(Fiducialups);
Fiducialdowns = np.array(Fiducialdowns);

#Mapping the image plane to reticle plane

for i in range(nfiducial):
    for j in range(4):
        Reticlefidup[i,j,0] = griddata(XYFieldheight, RealX2, (Fiducialups[i,j]),  method='linear');
        Reticlefidup[i,j,1] = griddata(XYFieldheight, RealY2, (Fiducialups[i,j]),  method='linear');
        Reticlefidown[i,j,0] = griddata(XYFieldheight, RealX2, (Fiducialdowns[i,j]),  method='linear');
        Reticlefidown[i,j,1] = griddata(XYFieldheight, RealY2, (Fiducialdowns[i,j]),  method='linear');

#covert mm to pixel 
Reticlefiduppix = np.array(Reticlefidup)*1000/res_print  + centercoor2;
Reticlefidownpix = np.array(Reticlefidown)*1000/res_print + centercoor2;

nfiducial = len(Reticlefidownpix);
#Generate the svg graph
dwg1 = svgwrite.Drawing(filename = 'reticleplane_slantededge.svg', size = (xres, yres))
#dwg.viewbox(width= Res_H, height= Res_V);

dwg1.add(dwg1.rect(insert=(0, 0), size=('100%', '100%'), fill='black'))

for i in range(nfiducial): 
    fidup = dwg1.polygon(points=[(Reticlefidownpix[i,0,0],Reticlefidownpix[i,0,1]),(Reticlefidownpix[i,1,0],Reticlefidownpix[i,1,1]),(Reticlefidownpix[i,2,0],Reticlefidownpix[i,2,1]),(Reticlefidownpix[i,3,0],Reticlefidownpix[i,3,1])], fill='white')
    fidown = dwg1.polygon(points=[(Reticlefiduppix[i,0,0],Reticlefiduppix[i,0,1]),(Reticlefiduppix[i,1,0],Reticlefiduppix[i,1,1]),(Reticlefiduppix[i,2,0],Reticlefiduppix[i,2,1]),(Reticlefiduppix[i,3,0],Reticlefiduppix[i,3,1])], fill='white')
    dwg1.add(fidup)
    dwg1.add(fidown)
dwg1.save()    