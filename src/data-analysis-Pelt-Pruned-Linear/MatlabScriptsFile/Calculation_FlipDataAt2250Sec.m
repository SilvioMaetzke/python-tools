clc;

% Load the speed data
load('speed_1.mat'); % or use your method to load the variable 'Spd'

% Define time step and cut index
dt = 0.1;% time step in seconds
cut_time = 2250;% time in seconds
cut_index = cut_time / dt;

% Rearrange the data
Spd_new = [Spd(cut_index+1:end); Spd(1:cut_index)];
Spd=Spd_new;
% Save the new data
save('speed_1_flipped.mat', 'Spd');

%repeat for SOC data
% Load the speed data
load('SOC_1.mat');% or use your method to load the variable 'Spd'

% Define time step and cut index already above for Spd
% dt = 0.1;              % time step in seconds
% cut_time = 2250;       % time in seconds
% cut_index = cut_time / dt;

% Rearrange the data
SOC_new = [SOC(cut_index+1:end); SOC(1:cut_index)];
SOC=SOC_new;
% Save the new data
save('SOC_1_flipped.mat', 'SOC');