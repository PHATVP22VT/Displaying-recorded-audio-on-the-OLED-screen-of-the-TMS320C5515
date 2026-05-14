% =========================================================
% BUOC 7: Gia lap man hinh OLED SSD1306 128x64
% Hien thi ket qua nhan dang giong het man hinh thuc
% =========================================================

clc; clear; close all;

% =========================================================
% Gia lap man hinh chao
% =========================================================
oled_fig = create_oled();
ax = gca;

oled_clear(ax);
oled_print(ax, 0, 0, 'Speech to OLED');
oled_print(ax, 0, 2, 'Waiting...');
oled_print(ax, 0, 5, 'TMS320C5515');
oled_print(ax, 0, 6, 'DSP Project');
drawnow;

fprintf('=== BUOC 7: OLED Gia lap ===\n');
fprintf('Man hinh chao dang hien thi...\n');
pause(2);

% =========================================================
% Load ket qua DTW va hien thi
% =========================================================
if exist('dtw_results.mat','file')
    load('dtw_results.mat');   % results_log

    % --- Load WORDS 1 lan duy nhat (tranh load lap trong vong lap) ---
    tmp   = load('templates.mat', 'templates');
    WORDS = fieldnames(tmp.templates);
    clear tmp;

    fprintf('Tim thay %d ket qua DTW, hien thi len OLED...\n\n', ...
            length(results_log));

    for i = 1:length(results_log)
        r    = results_log{i};
        word = r.word;

        fprintf('[OLED] Hien thi: "%s"\n', upper(word));
        oled_show_heard(ax, word);

        % Dong thoi hien thi thong tin ben canh
        figure('Name', sprintf('Ket qua %d/%d', i, length(results_log)), ...
               'NumberTitle','off', 'Position',[540 100 500 300]);

        % Bar chart DTW distance
        subplot(2,1,1);
        bar(r.all_dists, 'FaceColor',[0.3 0.6 1]);
        set(gca, 'XTickLabel', WORDS, 'XTick', 1:length(WORDS));
        ylabel('DTW Distance');
        title(sprintf('Nhan dang: "%s"', upper(word)));
        grid on;
        [~, bi] = min(r.all_dists);
        hold on;
        bar(bi, r.all_dists(bi), 'FaceColor',[0.1 0.9 0.3]);
        hold off;

        % Gia lap bar LED (giong mach Proteus)
        subplot(2,1,2);
        n_led = min(6, length(word));
        led_colors = repmat([0.2 0.2 0.2], 6, 1);   % mau toi = tat
        for li = 1:n_led
            led_colors(li,:) = [0.9 0.1 0.1];        % mau do = sang
        end
        hold on;
        for li = 1:6
            rectangle('Position', [li-0.4, 0, 0.8, 1], ...
                      'FaceColor', led_colors(li,:), ...
                      'EdgeColor', 'k', 'LineWidth', 1.5);
        end
        hold off;
        xlim([0 7]); ylim([0 1.5]);
        set(gca, 'XTick', 1:6, 'XTickLabel', ...
            {'PB0','PB1','PB2','PB3','PB4','PB5'});
        title(sprintf('Bar LED (gia lap %d ky tu dau)', length(word)));
        axis off; box off;

        pause(2);
    end

else
    % Demo voi chuoi thu cong khi chua co dtw_results.mat
    demo_words = {'Hello','Ready','Error','Complete','Temperature'};
    fprintf('Khong tim thay dtw_results.mat\n');
    fprintf('Chay demo voi cac tu mau...\n\n');

    for i = 1:length(demo_words)
        w = demo_words{i};
        fprintf('[OLED] Demo: "%s"\n', upper(w));
        oled_show_heard(ax, w);
        pause(1.5);
    end
end

fprintf('\n=== XONG BUOC 7 ===\n');
fprintf('Pipeline hoan chinh: step1 -> step2 -> step3 -> step4 -> step5 -> step6 -> step7\n');


% =========================================================
% LOCAL FUNCTIONS (phai dat cuoi file script)
% =========================================================

function oled_fig = create_oled()
% Tao figure gia lap man hinh OLED SSD1306 128x64
    oled_fig = figure('Name',   'OLED SSD1306 - 128x64', ...
                      'NumberTitle', 'off', ...
                      'Color',       [0.15 0.15 0.15], ...
                      'Position',    [100 100 420 260], ...
                      'Resize',      'off');
    axes('Position', [0.05 0.05 0.90 0.90], ...
         'Color',    'black', ...
         'XColor',   'none', ...
         'YColor',   'none', ...
         'XLim',     [0 128], ...
         'YLim',     [0 64]);
    hold on;
end

function oled_clear(ax)
% Xoa noi dung man hinh OLED (dat nen den)
    cla(ax);
    set(ax, 'Color', 'black');
end

function oled_print(ax, col, row, str, font_scale)
% In chu len OLED gia lap
% col: 0-20 (cot ky tu), row: 0-7 (dong, moi dong 8px)
    if nargin < 5
        font_scale = 1;
    end
    x_px = col * 6;
    y_px = 64 - (row * 8) - 8;
    text(ax, x_px, y_px, str, ...
         'Color',      'white', ...
         'FontName',   'Courier New', ...
         'FontSize',   7 * font_scale, ...
         'FontWeight', 'bold', ...
         'Units',      'data');
end

function oled_show_heard(ax, result_str)
% Hien thi ket qua nhan dang len OLED gia lap
    oled_clear(ax);
    % Dong 0: nhan "Heard:"
    oled_print(ax, 0, 0, 'Heard:');
    % Dong 2: tu duoc nhan dang (toi da 20 ky tu)
    display_str = upper(result_str(1:min(20, end)));
    oled_print(ax, 0, 2, display_str);
    % Dong 6: bar tin hieu gia lap
    oled_print(ax, 0, 6, '||||||||||||||||||||');
    drawnow;
end