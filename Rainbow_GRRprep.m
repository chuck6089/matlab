clear; clc;

%output file for GRR summary
outputGRR = 'H:\RB data\GRR_iDolphinRR_08242020.csv';

%Enter folder path and name for first operator
op1 = 'Alex';
dir1 = 'H:\RB data\AP GRR\';
GRR_op1 = dir(fullfile(dir1, '*.csv'));

%Enter folder path for first operator
op2 = 'Natalie';
dir2 = 'H:\RB data\NG GRR\';
GRR_op2 = dir(fullfile(dir2, '*.csv'));

for i=1:numel(GRR_op1)
    fullname = strcat(dir1, GRR_op1(i).name);
    data = readtable(fullname);
    data.Properties.VariableNames(17)={'MaxEff'};
    SampleID(i) = string(extractBefore(GRR_op1(i).name,"_repeat"));
    Operator(i) = string(op1);
    rb_max(i) = round(data.MaxEff(1),2);
end

for i=1:numel(GRR_op2)
    fullname = strcat(dir2, GRR_op2(i).name);
    data = readtable(fullname);
    data.Properties.VariableNames(17)={'MaxEff'};
    SampleID(i+numel(GRR_op1)) = string(extractBefore(GRR_op2(i).name,"_repeat"));
    Operator(i+numel(GRR_op1)) = string(op2);
    rb_max(i+numel(GRR_op1)) = round(data.MaxEff(1),2);
end

A = [(SampleID)',(Operator)',(rb_max)'];
T = array2table(A);
T.Properties.VariableNames(1:3) = {'SampleID', 'Operator', 'Max_RB_Eff'};
writetable(T,GRRfile);