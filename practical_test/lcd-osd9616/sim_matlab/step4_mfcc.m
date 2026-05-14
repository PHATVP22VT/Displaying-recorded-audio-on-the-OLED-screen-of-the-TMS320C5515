% =========================================================
% BUOC 4: MFCC - Mel Frequency Cepstral Coefficients
% Tuong duong: trich xuat dac trung tren DSP C5515
% =========================================================

clc; clear; close all;

load('fft_result.mat');
mag_spec = fft_result.mag_spec;
Fs       = fft_result.Fs;
N_FFT    = fft_result.N_FFT;
N_HALF   = fft_result.N_HALF;
N_FRAMES = fft_result.N_FRAMES;

% --- Thong so MFCC ---
N_MFCC    = 13;    % So he so MFCC
N_FILTERS = 26;    % So mel filter
F_LOW     = 300;   % Hz
F_HIGH    = Fs/2;  % Hz

fprintf('=== BUOC 4: MFCC ===\n');
fprintf('So he so MFCC : %d\n', N_MFCC);
fprintf('So mel filter : %d\n', N_FILTERS);

% --- Ham chuyen doi Hz <-> Mel ---
hz2mel = @(f) 2595 * log10(1 + f/700);
mel2hz = @(m) 700 * (10.^(m/2595) - 1);

% --- Tao mel filterbank ---
mel_low  = hz2mel(F_LOW);
mel_high = hz2mel(F_HIGH);
mel_pts  = linspace(mel_low, mel_high, N_FILTERS+2);
hz_pts   = mel2hz(mel_pts);
bin_pts  = floor((N_FFT+1) * hz_pts / Fs);

% Tao ma tran filterbank: N_FILTERS x N_HALF
filterbank = zeros(N_FILTERS, N_HALF);
for m = 1 : N_FILTERS
    for k = bin_pts(m) : bin_pts(m+1)
        if k >= 1 && k <= N_HALF
            filterbank(m,k) = (k - bin_pts(m)) / (bin_pts(m+1) - bin_pts(m));
        end
    end
    for k = bin_pts(m+1) : bin_pts(m+2)
        if k >= 1 && k <= N_HALF
            filterbank(m,k) = (bin_pts(m+2) - k) / (bin_pts(m+2) - bin_pts(m+1));
        end
    end
end

% --- Tinh MFCC cho toan bo frames ---
% filterbank x mag_spec -> N_FILTERS x N_FRAMES
filter_out = filterbank * mag_spec;          % N_FILTERS x N_FRAMES
log_filter = log(filter_out + 1e-10);        % Log energy

% DCT -> lay N_MFCC he so dau
mfcc_all = zeros(N_MFCC, N_FRAMES);
for i = 1 : N_FRAMES
    dct_out = dct(log_filter(:,i));
    mfcc_all(:,i) = dct_out(1:N_MFCC);
end

fprintf('[OK] MFCC shape: %dx%d (he_so x frames)\n', N_MFCC, N_FRAMES);

% --- Ve ---
figure('Name','Buoc 4 - MFCC','NumberTitle','off');

% Plot 1: Mel filterbank
subplot(3,1,1);
freqs = (0:N_HALF-1)*Fs/N_FFT;
plot(freqs/1000, filterbank', 'LineWidth', 0.8);
xlabel('Tan so (kHz)'); ylabel('Bien do');
title(sprintf('Mel Filterbank (%d filters, %d Hz - %d Hz)', N_FILTERS, F_LOW, F_HIGH));
grid on;

% Plot 2: MFCC cua 1 frame dien hinh
mid = round(N_FRAMES/2);
subplot(3,1,2);
stem(1:N_MFCC, mfcc_all(:,mid), 'Color',[0.2 0.7 1], ...
     'MarkerFaceColor',[0.2 0.7 1], 'LineWidth', 1.5);
xlabel('He so MFCC thu n'); ylabel('Gia tri');
title(sprintf('MFCC cua frame %d (vung co tieng noi)', mid));
grid on;

% Plot 3: MFCC theo thoi gian (tat ca frames)
subplot(3,1,3);
t_frames = (0:N_FRAMES-1) * 128 / Fs;
imagesc(t_frames, 1:N_MFCC, mfcc_all);
axis xy; colormap('jet'); colorbar;
xlabel('Thoi gian (s)'); ylabel('He so MFCC');
title('MFCC toan bo tin hieu (dau vao cho DTW)');

% --- Luu ---
mfcc_result.mfcc_all   = mfcc_all;
mfcc_result.filterbank = filterbank;
mfcc_result.N_MFCC     = N_MFCC;
mfcc_result.N_FRAMES   = N_FRAMES;
mfcc_result.Fs         = Fs;
save('mfcc_result.mat', 'mfcc_result');
fprintf('[SAVE] Da luu: mfcc_result.mat\n');
fprintf('\nXong buoc 4! Chay step5_template.m de tiep tuc.\n');