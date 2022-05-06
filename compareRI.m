flatfield_1 = importdata('G:\Shared drives\Display & Optics\Test & Integration\Metrology system\Waveguide Metrology\IQTester\IQT5\calibrations\flatfield measurement_10142021\flatfield data\ND2\3mm_aperture_blue_ND2.txt');
flatfield_2 = importdata('G:\Shared drives\Display & Optics\Test & Integration\Metrology system\Waveguide Metrology\IQTester\IQT5\calibrations\flatfield measurement_10142021\flatfield data\ND2\2mm_aperture_blue_ND2.txt');


comparemat = flatfield_2.data./flatfield_1.data;

comparematfilter = filt(comparemat,0,2);

reducedmat = comparemat(200:end-200,200:end-200);

function filtered = filt(mat,low,high)
    [m,n] = size(mat);
    filtered = mat;
    for i = 1:m
        for j = 1:n
            if mat(m,n) > high || mat(m,n) < low
                %mat(m,n) = mean([mat(m-1,n),mat(m+1,n),mat(m,n-1),mat(m,n+1)]);\
                mat(m,n) = 0.5;
            end
        end
    end
end