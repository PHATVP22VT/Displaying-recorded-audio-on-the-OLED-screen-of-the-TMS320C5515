% =========================================================
% BUOC 2: Framing + Hamming window
% Tuong duong: xu ly frame trong DSP core C5515
% =========================================================

clc; clear; close all;

% --- Load du lieu buoc 1 ---
load('audio_recorded.mat');
x  = audio.samples_n;   % Tin hieu chuan hoa
Fs = audio.Fs;

% --- Thong so frame ---
FRAME_SIZE = 256;        % 256 samples = 16ms @ 16kHz
HOP_SIZE   = 128;        % Buoc nhay 128 = overlap 50%
N_FRAMES   = floor((length(x) - FRAME_SIZE) / HOP_SIZE) + 1;

fprintf('=== BUOC 2: Framing + Windowing ===\n');
fprintf('Frame size : %d samples (%.1f ms)\n', FRAME_SIZE, FRAME_SIZE/Fs*1000);
fprintf('Hop size   : %d samples (%.1f ms)\n', HOP_SIZE,   HOP_SIZE/Fs*1000);
fprintf('So frames  : %d\n', N_FRAMES);

% --- Tao Hamming window ---
win = hamming(FRAME_SIZE, 'periodic');

% --- Chia frame va ap window ---
frames = zeros(FRAME_SIZE, N_FRAMES);
for i = 1 : N_FRAMES
    idx_start = (i-1) * HOP_SIZE + 1;
    idx_end   = idx_start + FRAME_SIZE - 1;
    frames(:, i) = x(idx_start:idx_end) .* win;
end

fprintf('[OK] Chia thanh %d frames\n', N_FRAMES);

% --- Ve minh hoa ---
figure('Name','Buoc 2 - Framing + Hamming','NumberTitle','off');

% Plot 1: Tin hieu goc
subplot(3,1,1);
t = (0:length(x)-1) / Fs;
plot(t, x, 'Color',[0.2 0.6 1]);
title('Tin hieu goc');
xlabel('Thoi gian (s)'); ylabel('Bien do');
grid on;

% Plot 2: Hamming window
subplot(3,1,2);
plot(win, 'Color',[1 0.5 0], 'LineWidth', 1.5);
title(sprintf('Hamming window (%d samples)', FRAME_SIZE));
xlabel('Sample'); ylabel('Bien do');
grid on;

% Plot 3: Minh hoa 3 frame giua (vung co tieng noi)
subplot(3,1,3);
mid = round(N_FRAMES / 2);
colors = {[0.2 0.8 0.4], [1 0.3 0.3], [0.5 0.3 1]};
hold on;
for k = -1 : 1
    fi = mid + k;
    if fi >= 1 && fi <= N_FRAMES
        plot(frames(:, fi), 'Color', colors{k+2}, ...
             'DisplayName', sprintf('Frame %d', fi));
    end
end
hold off;
legend('show');
title('3 frame lien tiep (sau khi ap Hamming window)');
xlabel('Sample trong frame'); ylabel('Bien do');
grid on;

% --- Luu ---
framing.frames     = frames;
framing.win        = win;
framing.N_FRAMES   = N_FRAMES;
framing.FRAME_SIZE = FRAME_SIZE;
framing.HOP_SIZE   = HOP_SIZE;
framing.Fs         = Fs;
save('framing_result.mat', 'framing');
fprintf('[SAVE] Da luu: framing_result.mat\n');
fprintf('\nXong buoc 2! Chay step3_fft.m de tiep tuc.\n');