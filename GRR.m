
%[file,path] = uigetfile({'*.csv';'*.xls'});

path = 'C:\Users\XZD6089\Desktop\Data\MTF\MTF2\GRR\05032022_after dome&aperture upgrade\';
file = 'GRRdata_05032022_MTF2 after upgrade.xlsx';

[~,~,rawdata]=xlsread(strcat(path,file));



rawdata = cell2table(rawdata(2:end,:),'VariableNames',rawdata(1,:));
%filter the rawdata
%index1 = (("red" == rawdata.LEDcolor)& ("RedRight" == rawdata.WGColor));

%filter = strcmpi("blue",rawdata.LEDcolor) & strcmpi("BlueRight",rawdata.WGColor);
filter = strcmpi("Red",rawdata.Wgcolor) & strcmpi("Manual",rawdata.Alignment);
%filter = strcmpi("Indv. Darkfield, calculated contrast",rawdata.Dark_Calibr) & strcmpi("Red",rawdata.Wgcolor);

rawdata = rawdata(filter,:);


%y = table2array(rawdata(:,10));
%y = rawdata.Meancontrast_red;
y = rawdata.spatialuniformity_red;
%y = rawdata.TP_red;
%y = rawdata.Centercontrast_red;
%y = rawdata.CRA_y_arcmin;
%part = table2array(rawdata(:,1));
part = rawdata.sampleID;
%operator = table2array(rawdata(:,4));
operator = rawdata.Operator;

[TABLE, stats] = gagerr(y,{part, operator},'randomoperator',true,'model','interaction','printgraph','off');

TABLE(:,4) = TABLE(:,3)*6;

TABLE(7,1) = stats.ndc;
TABLE(8,1) = stats.prr
%stats.ndc