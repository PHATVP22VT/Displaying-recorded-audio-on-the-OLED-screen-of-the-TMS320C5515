% =========================================================
% BUOC 6: DTW - Nhan dang giong noi
% Tuong duong: thuat toan DTW chay tren DSP core C5515
% =========================================================

clc; clear; close all;

load('templates.mat');   % templates, filterbank, win

Fs         = 16000;
N_BITS     = 16;
DURATION   = 2;
FRAME_SIZE = 256;
HOP_SIZE   = 128;
N_MFCC     = 13;

WORDS = fieldnames(templates);
fprintf('=== BUOC 6: DTW Nhan dang ===\n');
fprintf('Co %d tu trong thu vien: %s\n\n', length(WORDS), strjoin(WORDS,', '));

% --- Vong lap nhan dang ---
rec = audiorecorder(Fs, N_BITS, 1);
results_log = {};

while true
    fprintf('\nNhan Enter de noi (hoac go q + Enter de thoat)...\n');
    inp = input('', 's');
    if strcmpi(strtrim(inp), 'q')
        break;
    end

    fprintf('[REC] Dang nghe... NOI NGAY!\n');
    recordblocking(rec, DURATION);
    fprintf('[OK]  Ghi xong, dang nhan dang...\n');

    samples   = getaudiodata(rec, 'int16');
    samples_n = double(samples) / 32768;

    % Tinh MFCC cho am thanh vua ghi
    mfcc_input = compute_mfcc(samples_n, win, filterbank, ...
                               FRAME_SIZE, HOP_SIZE, N_MFCC);

    % So sanh DTW voi tung template
    best_word = '';
    best_dist = inf;
    all_dists = zeros(1, length(WORDS));

    for wi = 1:length(WORDS)
        word      = WORDS{wi};
        mfcc_tmpl = templates.(word).mfcc;
        d         = dtw_distance(mfcc_input, mfcc_tmpl);
        all_dists(wi) = d;
        if d < best_dist
            best_dist = d;
            best_word = word;
        end
    end

    fprintf('\n--- Ket qua DTW ---\n');
    for wi = 1:length(WORDS)
        marker = '';
        if strcmp(WORDS{wi}, best_word), marker = ' <-- BEST'; end
        fprintf('  %-15s: %.4f%s\n', WORDS{wi}, all_dists(wi), marker);
    end
    fprintf('=> Nhan dang: "%s" (dist=%.4f)\n', upper(best_word), best_dist);

    % Luu ket qua
    results_log{end+1} = struct('word', best_word, 'dist', best_dist, ...
                                 'all_dists', all_dists);

    % Ve ket qua
    figure('Name', sprintf('DTW Result: %s', upper(best_word)), ...
           'NumberTitle','off');
    subplot(2,1,1);
    t = (0:length(samples_n)-1)/Fs;
    plot(t, samples_n, 'Color',[0.2 0.6 1]);
    title(sprintf('Am thanh vua noi -> Nhan dang: "%s"', upper(best_word)));
    xlabel('Thoi gian (s)'); grid on;

    subplot(2,1,2);
    bar(all_dists, 'FaceColor',[0.3 0.7 1]);
    set(gca, 'XTickLabel', WORDS, 'XTick', 1:length(WORDS));
    ylabel('DTW distance (thap = giong hon)');
    title('Khoang cach DTW voi tung template');
    grid on;
    [~, bi] = min(all_dists);
    hold on;
    bar(bi, all_dists(bi), 'FaceColor',[0.1 0.9 0.3]);
    hold off;
end

save('dtw_results.mat', 'results_log');
fprintf('\n[SAVE] Da luu dtw_results.mat\n');
fprintf('Xong buoc 6! Chay step7_oled_display.m de tiep tuc.\n');


% =========================================================
% LOCAL FUNCTIONS (phai dat cuoi file script)
% =========================================================

function mfcc = compute_mfcc(samples_n, win, filterbank, ...
                              FRAME_SIZE, HOP_SIZE, N_MFCC)
% Tinh MFCC tu mang samples da chuan hoa
    n_frames = floor((length(samples_n) - FRAME_SIZE) / HOP_SIZE) + 1;
    N_HALF   = FRAME_SIZE/2 + 1;
    mfcc     = zeros(N_MFCC, n_frames);
    for fi = 1:n_frames
        s     = (fi-1)*HOP_SIZE + 1;
        frame = samples_n(s : s+FRAME_SIZE-1) .* win;
        X     = fft(frame, FRAME_SIZE);
        mag   = abs(X(1:N_HALF));
        fout  = filterbank * mag;
        lf    = log(fout + 1e-10);
        dc    = dct(lf);
        mfcc(:,fi) = dc(1:N_MFCC);
    end
end

function dist = dtw_distance(seq1, seq2)
% DTW distance chuan hoa theo tong do dai 2 chuoi
% seq1, seq2: N_MFCC x N_frames
    T = size(seq1, 2);
    R = size(seq2, 2);

    % Ma tran chi phi cuc bo
    d = zeros(T, R);
    for ti = 1:T
        for ri = 1:R
            d(ti,ri) = sum((seq1(:,ti) - seq2(:,ri)).^2);
        end
    end

    % Quy hoach dong DTW
    D = inf(T+1, R+1);
    D(1,1) = 0;
    for ti = 1:T
        for ri = 1:R
            cost        = d(ti,ri);
            D(ti+1,ri+1) = cost + min([D(ti, ri+1), D(ti+1, ri), D(ti, ri)]);
        end
    end

    dist = D(T+1, R+1) / (T + R);   % Chuan hoa theo do dai
end