%  [file,path] = uigetfile('*.xml');
%   filename = [path,file];

nofcameras = 5;
nofsamples = 6;
nofexits = 5;

filename = 'C:\Users\xzd6089\Dropbox (Facebook)\TriOptics data\XML\2019_12_19_15_41_06_admin_19B175_03_try3_dolphin_red_wafer_red_green_chaunee.xml';
   [data,color] = getmtfcradata1(filename,1,1,1,1,"LSF_x")
  for i = 1:nofcameras
      for j = 1:nofsamples
          for k = 1:nofexits
            
          end
      end
  end
  
  
  function [data,color] = getmtfcradata1(xmlfile,sample,exit,config,camera,datatype)
    expr = '^-([1-9]/d*/./d*|0/./d*[1-9]/d*)$';
    xml = xmlread(xmlfile);
    exportdata = xml.getElementsByTagName('exported_data');
    header = exportdata.item(0).getElementsByTagName('header');
    setup = header.item(0).getElementsByTagName('setup');
    color = char(setup.item(0).getAttribute('color'));
    measurements = exportdata.item(0).getElementsByTagName('measurements');
    samples = measurements.item(0).getElementsByTagName('sample');
    exits = samples.item(sample-1).getElementsByTagName('exit');
    configs = exits.item(exit-1).getElementsByTagName('config');
    cameras = configs.item(config-1).getElementsByTagName('camera');
    switch datatype
        case "MTF_x"
            index = camera-1;
            data = string(cameras.item(index).getAttribute('sag_curve'));
            data = strsplit(data,',');
            data = str2double(data);
        case "MTF_y"
            index = camera-1;
            data = string(cameras.item(index).getAttribute('tan_curve'));
            data = strsplit(data,',');
            data = str2double(data);
        case "LSF_x"
            index = camera - 1;
            data = char(cameras.item(index).getAttribute('sag_lsf'));
            data = regexp(data,'\{\{(?<index>\d+)\}\{(?<value>.{1,10})\}\{(?<angle>.{1,10})\}\};','names');
%             data = regexp(data,expr,'match');
        case "LSF_y"
            index = camera - 1;
            data = char(cameras.item(index).getAttribute('tan_lsf'));
            data = regexp(data,expr,'match');
            data = regexp(data,'\{\{(?<index>\d+)\}\{(?<value>.{1,10})\}\{(?<angle>.{1,10})\}\};','names');
        case "CRA_x"
            index = camera-1+5;
            data = cameras.item(index).getAttribute('cra_dx');
            data = str2double(data);
        case "CRA_y"
            index = camera -1 +5;
            data = cameras.item(index).getAttribute('cra_dy');
            data = str2double(data);
        otherwise
            data = "";
             warning('Unrecongnizable datatype');
    end
  end