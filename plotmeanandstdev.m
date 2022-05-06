folder = 'C:\Users\xzd6089\Desktop\try\Darkfield_VW50MP_04052022\04122022\average\500ms';
%folder = 'C:\Users\xzd6089\Desktop\try\Darkfield_VW29MP_032022\03302022\10ms';
folder = 'G:\Shared drives\Display & Optics\Test & Integration\Metrology system\Waveguide Metrology\Gen2 tools\IQT\camera test\IMX324\GT6400_one_week_test\GT6400_one_week_test\Images_three_days';
userpath(folder);
fileList = [dir(fullfile(folder, '*.tiff')),dir(fullfile(folder, '*.tif'))];
fileList = fileList(~[fileList.isdir]);
[~,idx] = sort([fileList.datenum]);
fileList = fileList(idx);

n = length(fileList);
means = zeros(1,n); stdevs = zeros(1,n);


for i = 1:n
    filename = [fileList(i).folder,'\',fileList(i).name];
    IM = imread(filename);
    means(i) = mean(double(IM(:)));
    stdevs(i) = std(double(IM(:)));
end

x = 1:n;

e = errorbar(x,means,stdevs);
xlim([0 n+1]); xlabel('Frame#'); ylabel('pixel value');
xlabel('Time');
e.Marker = '*';
e.MarkerSize = 10;
e.Color = 'blue';
e.MarkerEdgeColor = 'red';
e.MarkerFaceColor = 'red';
e.CapSize = 15;

saveas(e,[folder,'\Plot.png'])