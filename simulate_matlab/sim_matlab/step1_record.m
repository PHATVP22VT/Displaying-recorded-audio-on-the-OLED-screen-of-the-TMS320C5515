% =========================================================
% BUOC 1: Thu am tu mic PC
% Tuong duong: Tai nghe mic -> Stereo In -> ADC tren C5515
% =========================================================

clc; clear; close all;

% --- Thong so ---
Fs          = 16000;   % Sample rate 16kHz (giong C5515)
N_BITS      = 16;      % 16-bit PCM
N_CHANNELS  = 1;       % Mono
DURATION    = 2;       % Ghi am 2 giay

fprintf('=== BUOC 1: Thu am ===\n');
fprintf('Sample rate : %d Hz\n', Fs);
fprintf('Duration    : %d giay\n', DURATION);
fprintf('\nNhan Enter de bat dau ghi am...\n');
pause;

% --- Ghi am ---
rec = audiorecorder(Fs, N_BITS, N_CHANNELS);
fprintf('[REC] Dang ghi am... Noi vao mic!\n');
recordblocking(rec, DURATION);
fprintf('[OK]  Ghi am xong!\n');

% --- Lay du lieu PCM ---
samples = getaudiodata(rec, 'int16');   % int16 giong ADC C5515
samples_norm = double(samples) / 32768; % Chuan hoa -1..+1 de xu ly

% --- Ve tin hieu ---
t = (0 : length(samples)-1) / Fs;

figure('Name', 'Buoc 1 - Tin hieu thu am', 'NumberTitle', 'off');

subplot(2,1,1);
plot(t, samples_norm, 'Color', [0.2 0.6 1]);
xlabel('Thoi gian (s)');
ylabel('Bien do');
title('Tin hieu am thanh (Stereo In gia lap)');
grid on;

subplot(2,1,2);
spectrogram(samples_norm, 256, 128, 256, Fs, 'yaxis');
title('Spectrogram');
colormap('jet');

% --- Luu lai de buoc sau dung ---
audio.samples   = samples;
audio.samples_n = samples_norm;
audio.Fs        = Fs;
audio.duration  = DURATION;
save('audio_recorded.mat', 'audio');
fprintf('[SAVE] Da luu: audio_recorded.mat\n');
fprintf('\nXong buoc 1! Chay step2_framing.m de tiep tuc.\n');
