% =========================================================
% BUOC 5: Thu template - Ghi am tung tu de DTW so khop
% Chay file nay 1 lan duy nhat de tao thu vien mau
% =========================================================

clc; clear; close all;

% --- Danh sach tu can thu ---
WORDS = {'hello', 'temperature', 'ready', 'error', 'complete'};

Fs         = 16000;
N_BITS     = 16;
DURATION   = 2;
FRAME_SIZE = 256;
HOP_SIZE   = 128;
N_MFCC     = 13;
N_FILTERS  = 26;
F_LOW      = 300;
F_HIGH     = Fs/2;

fprintf('=== BUOC 5: Thu template cho DTW ===\n');
fprintf('Ban se noi %d tu, moi tu ghi %d giay\n\n', length(WORDS), DURATION);

% --- Xay dung mel filterbank ---
hz2mel     = @(f) 2595 * log10(1 + f/700);
mel2hz     = @(m) 700 * (10.^(m/2595) - 1);
mel_low    = hz2mel(F_LOW);
mel_high   = hz2mel(F_HIGH);
mel_pts    = linspace(mel_low, mel_high, N_FILTERS+2);
hz_pts     = mel2hz(mel_pts);
bin_pts    = floor((FRAME_SIZE+1) * hz_pts / Fs);
N_HALF     = FRAME_SIZE/2 + 1;
filterbank = zeros(N_FILTERS, N_HALF);
for m = 1:N_FILTERS
    for k = bin_pts(m):bin_pts(m+1)
        if k >= 1 && k <= N_HALF
            filterbank(m,k) = (k - bin_pts(m)) / (bin_pts(m+1) - bin_pts(m));
        end
    end
    for k = bin_pts(m+1):bin_pts(m+2)
        if k >= 1 && k <= N_HALF
            filterbank(m,k) = (bin_pts(m+2) - k) / (bin_pts(m+2) - bin_pts(m+1));
        end
    end
end
win = hamming(FRAME_SIZE, 'periodic');

% --- Ghi am tung tu ---
templates = struct();
rec = audiorecorder(Fs, N_BITS, 1);

for wi = 1 : length(WORDS)
    word = WORDS{wi};
    fprintf('--- Tu %d/%d: "%s" ---\n', wi, length(WORDS), upper(word));
    fprintf('Nhan Enter roi noi ngay vao mic...\n');
    pause;

    fprintf('[REC] Dang ghi... NOI NGAY!\n');
    recordblocking(rec, DURATION);
    fprintf('[OK]  Xong!\n');

    samples   = getaudiodata(rec, 'int16');
    samples_n = double(samples) / 32768;

    % Tinh MFCC lam template
    mfcc_tmpl = compute_mfcc(samples_n, win, filterbank, ...
                              FRAME_SIZE, HOP_SIZE, N_MFCC);

    % Luu vao struct
    templates.(word).mfcc     = mfcc_tmpl;
    templates.(word).samples  = samples_n;
    templates.(word).n_frames = size(mfcc_tmpl, 2);

    fprintf('[OK] Template "%s": %d frames MFCC\n\n', word, size(mfcc_tmpl,2));

    % Ve kiem tra nhanh
    figure('Name', sprintf('Template - %s', upper(word)), 'NumberTitle','off');
    subplot(2,1,1);
    t = (0:length(samples_n)-1)/Fs;
    plot(t, samples_n, 'Color',[0.2 0.6 1]);
    title(sprintf('Tin hieu: "%s"', upper(word)));
    xlabel('Thoi gian (s)'); grid on;
    subplot(2,1,2);
    imagesc(mfcc_tmpl); axis xy; colormap('jet');
    title('MFCC template'); xlabel('Frame'); ylabel('He so');
    colorbar;
end

% --- Luu tat ca template ---
save('templates.mat', 'templates', 'filterbank', 'win');
fprintf('=== XONG! Da luu templates.mat ===\n');
fprintf('Co %d templates: %s\n', length(WORDS), strjoin(WORDS,', '));
fprintf('\nChay step6_dtw_recognize.m de nhan dang.\n');


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