% =========================================================
% BUOC 3: FFT - Phan tich pho tan so
% Tuong duong: FFT 256-point chay tren DSPLIB cua C5515
% =========================================================

clc; clear; close all;

% --- Load du lieu buoc 2 ---
load('framing_result.mat');
frames     = framing.frames;
Fs         = framing.Fs;
FRAME_SIZE = framing.FRAME_SIZE;
N_FRAMES   = framing.N_FRAMES;

fprintf('=== BUOC 3: FFT ===\n');
fprintf('FFT size  : %d point\n', FRAME_SIZE);
fprintf('So frames : %d\n', N_FRAMES);

% --- Tinh FFT cho toan bo frames ---
N_FFT  = FRAME_SIZE;          % 256-point FFT
N_HALF = N_FFT/2 + 1;         % Chi lay nua duong pho (0 -> Fs/2)
freqs  = (0:N_HALF-1) * Fs / N_FFT;  % Truc tan so Hz

% Ma tran luu magnitude spectrum: N_HALF x N_FRAMES
mag_spec = zeros(N_HALF, N_FRAMES);

for i = 1 : N_FRAMES
    X = fft(frames(:,i), N_FFT);
    mag_spec(:,i) = abs(X(1:N_HALF));
end

% Chuyen sang dB (log scale - giong xu ly tren DSP)
log_spec = 20 * log10(mag_spec + 1e-10);

fprintf('[OK] Tinh FFT xong cho %d frames\n', N_FRAMES);

% --- Ve ---
figure('Name','Buoc 3 - FFT Spectrum','NumberTitle','off');

% Plot 1: Spectrum cua 1 frame dien hinh (frame giua - vung co tieng)
mid = round(N_FRAMES / 2);
subplot(3,1,1);
plot(freqs/1000, log_spec(:, mid), 'Color',[0.2 0.8 0.4], 'LineWidth',1.2);
xlabel('Tan so (kHz)'); ylabel('Bien do (dB)');
title(sprintf('Pho FFT - Frame %d (vung co tieng noi)', mid));
xlim([0 Fs/2/1000]); grid on;

% Plot 2: So sanh frame co tieng vs frame im lang
quiet_frame = 10;   % Frame gan dau = im lang
subplot(3,1,2);
hold on;
plot(freqs/1000, log_spec(:, quiet_frame), 'Color',[0.6 0.6 0.6], ...
     'LineWidth',1, 'DisplayName','Im lang');
plot(freqs/1000, log_spec(:, mid), 'Color',[1 0.4 0.1], ...
     'LineWidth',1.2, 'DisplayName','Co tieng noi');
hold off;
xlabel('Tan so (kHz)'); ylabel('Bien do (dB)');
title('So sanh pho: Im lang vs Co tieng noi');
xlim([0 Fs/2/1000]); grid on; legend('show');

% Plot 3: Spectrogram toan bo (nhu OLED hien thi truc quan)
subplot(3,1,3);
t_frames = (0:N_FRAMES-1) * framing.HOP_SIZE / Fs;
imagesc(t_frames, freqs/1000, log_spec);
axis xy;
xlabel('Thoi gian (s)'); ylabel('Tan so (kHz)');
title('Spectrogram toan bo (FFT tat ca frames)');
colormap('jet'); colorbar;
caxis([-100 0]);

% --- Luu ---
fft_result.mag_spec  = mag_spec;
fft_result.log_spec  = log_spec;
fft_result.freqs     = freqs;
fft_result.N_FFT     = N_FFT;
fft_result.N_HALF    = N_HALF;
fft_result.N_FRAMES  = N_FRAMES;
fft_result.Fs        = Fs;
save('fft_result.mat', 'fft_result');
fprintf('[SAVE] Da luu: fft_result.mat\n');
fprintf('\nXong buoc 3! Chay step4_mfcc.m de tiep tuc.\n');