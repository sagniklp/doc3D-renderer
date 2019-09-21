% fm2bm - Call uv2mp in parallel
% Author: Sagnik Das

src_dir = '../uvmat/1/';
dst_dir = '../bm/1/';

files=dir(src_dir);
n=length(files);
% the loop should be modified based on how you organize your images

parfor k = 1 : n
    % check if the output directory exists, otherwise, create one
    %t = fullfile(dst_dir, int2str(fid));
    t=dst_dir;
    if ~exist(t, 'dir')
        mkdir(t);
    end
    currf=files(k).name;
    if contains(currf,'.mat')
        fname = fullfile(src_dir, currf);
        disp(k);
        d = load(fname);
        % read uv
        uv = d.uv;
        uv = im2single(uv);
        % flip v
        uv = cat(3, uv(:, :, 3), 1.0 - uv(:, :, 2), uv(:, :, 1));
        % compute backward mapping
        bm = uv2mp(uv);
        % save file (function save cannot be used with parfor, but the following can)
        m=matfile(fullfile(t, currf), 'writable', true);
        m.bm = bm;
    end
end
