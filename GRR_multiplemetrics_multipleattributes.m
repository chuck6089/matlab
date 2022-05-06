%5/28/2021
%Author: Zhida Xu
%[file,path] = uigetfile({'*.csv';'*.xls'});

path = 'C:\Users\XZD6089\Desktop\Data\MTF\MTF2\GRR\05032022_after dome&aperture upgrade\';
file = 'GRRdata_05032022_MTF2 after upgrade.xlsx';

[~,~,rawdata]=xlsread(strcat(path,file));

datacolumn = {'MTF30_x','MTF30_y','MTF_x_7p5lp','MTF_y_7p5lp','CRA_x_arcmin','CRA_y_arcmin'};
%datacolumn = {'CRA_x_arcmin_red_exit1_camera1','CRA_y_arcmin_red_exit1_camera1',};

%loopcolumn = {'Colorside','Color','Exitnumber','Cameranumber'};
loopcolumn = {'color','eyeside'};

partcolumn = 'Barcode';
operatorcolumn = 'operator';

rawdata = cell2table(rawdata(2:end,:),'VariableNames',rawdata(1,:));

nofdatacolumn = length(datacolumn);

nofloopcolumn = length(loopcolumn);

uniquevalue = cell(1,nofloopcolumn);

nofuniquevalue = ones(1,nofloopcolumn);
iofuniquevalue = ones(1,nofloopcolumn);

nofloops = 1;


%            GRRvariationTab =  array2table(zeros(1,nofdatacolumn+1), 'VariableNames',['config',datacolumn]);
%            RepeatabilityTab = array2table(zeros(1,nofdatacolumn+1), 'VariableNames',['config',datacolumn]);
%            ReproduceTab = array2table(zeros(1,nofdatacolumn+1), 'VariableNames',['config',datacolumn]);
%            NDCTab = array2table(zeros(1,nofdatacolumn+1), 'VariableNames',['config',datacolumn]);
%            PRRTab = array2table(zeros(1,nofdatacolumn+1), 'VariableNames',['config',datacolumn]);
% 
%            PRRTab.config = num2str(PRRTab.config); 
%            RepeatabilityTab.config = num2str(RepeatabilityTab.config); 
%            ReproduceTab.config = num2str(ReproduceTab.config); 
%            NDCTab.config = num2str(NDCTab.config); 
%            GRRvariationTab.config = num2str(GRRvariationTab.config); 

GRRvariationTab = ['TestID',datacolumn];
RepeatabilityTab = ['TestID',datacolumn];
ReproduceTab = ['TestID',datacolumn];
NDCTab = ['TestID',datacolumn];
PRRTab = ['TestID',datacolumn];

for i = 1:nofloopcolumn
    uniquevalue{i} = unique(rawdata.(loopcolumn{i}));
    nofuniquevalue(i) = length(uniquevalue{i});
    nofloops = nofloops*nofuniquevalue(i);
end

% filter1 = strcmpi("AM",rawdata.Operator)
% rawdata = rawdata(filter1,:);

for i = 1:nofloops
    
    % Total Variance%: TABLE(1,2), Repeatability variance%: TABLE(2,2), Reproducibility variance%: TABLE(3,2)  
    % Part variance%: TABLE(6,2)
    % NDC = stats.ndc, PRR = stats.prr

    filter =  getfilter(rawdata,loopcolumn{1},select(uniquevalue,1,iofuniquevalue(1)));
    
    
    configstring =  '';
    
    for m = 1:nofloopcolumn
        filter = filter & getfilter(rawdata,loopcolumn{m},select(uniquevalue,m,iofuniquevalue(m)));
        configstring = strcat(configstring,'_',loopcolumn{m},'_',num2str(select(uniquevalue,m,iofuniquevalue(m))));
    end
   
    
    filteredata = rawdata(filter,:);
    configstring = configstring(2:end)
    
            GRRvariation = {configstring};
            Repeatability = {configstring};
            Reproduce = {configstring};
            NDC = {configstring};
            PRR = {configstring};
    
    if ~isempty(filteredata)
        for k = 1:nofdatacolumn
            part = filteredata.(partcolumn);
            operator = filteredata.(operatorcolumn);
            y = filteredata.(datacolumn{k});
            [TABLE, stats] = gagerr(y,{part, operator},'randomoperator',true,'model','interaction','printgraph','off');
            GRRvariation = [GRRvariation,TABLE(1,2)];
            Repeatability = [Repeatability,TABLE(2,2)];
            Reproduce = [Reproduce,TABLE(3,2)];
            NDC = [NDC,stats.ndc];
            PRR = [PRR,stats.prr];
        end

    else
            GRRvariation = [GRRvariation,num2cell(NaN(1,nofdatacolumn))];
            Repeatability = [Repeatability,num2cell(NaN(1,nofdatacolumn))];
            Reproduce = [Reproduce,num2cell(NaN(1,nofdatacolumn))];
            NDC = [NDC,num2cell(NaN(1,nofdatacolumn))];
            PRR = [PRR,num2cell(NaN(1,nofdatacolumn))];
    end
    
        GRRvariationTab = [GRRvariationTab; GRRvariation];
        RepeatabilityTab = [RepeatabilityTab;Repeatability];
        ReproduceTab = [ReproduceTab;Reproduce];
        NDCTab = [NDCTab;NDC];
        PRRTab = [PRRTab;PRR];

    
    
    if i == nofloops
        break;
    end
    iofuniquevalue(nofloopcolumn) = iofuniquevalue(nofloopcolumn) + 1;
    for j = nofloopcolumn:-1:1
        if iofuniquevalue(j) >  nofuniquevalue(j)
            iofuniquevalue(j) = 1;
            iofuniquevalue(j-1) = iofuniquevalue(j-1) + 1;
        end
    end
end

%save to XLS with different tabs for variation%, NDC, and PRR
xlsfilename = 'GRRresult.xls';
filename = strcat(path,xlsfilename);
xlswrite(filename,GRRvariationTab,'GRRvariation%');
xlswrite(filename,RepeatabilityTab,'Repeatability%');
xlswrite(filename,ReproduceTab,'Reproducibility%');
xlswrite(filename,NDCTab,'NDC');
xlswrite(filename,PRRTab,'PRR%');


function data = select(M,i,j)  %M is cell
     if iscell(M{i})
         data = M{i}{j};
     else
         data = M{i}(j);
     end
end

function filter = getfilter(M,indexchar,input)
     if ischar(input)
         filter = strcmpi(input,M.(indexchar));
     else
         filter = (M.(indexchar) == input);
     end
end
