[file,path] = uigetfile('*.png');
FileName = [path,file];
Data = imread(FileName);
fid1 = fopen(FileName);
fseek(fid1,41,'bof');
offset = 16-fread(fid1,1);
Data = bitshift(Data,-offset);
