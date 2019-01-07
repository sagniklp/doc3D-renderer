% input directory and output directory
src_dir = '/nfs/detection/kema/data/docwarp/fm1';
dst_dir = '/nfs/detection/kema/data/docwarp/bm1';

% the loop should be modified based on how you organize your images
for fid = 6 : 20
    parfor k = 1 : 5200
        % check if the output directory exists, otherwise, create one
        t = fullfile(dst_dir, int2str(fid));
        if ~exist(t, 'dir')
            mkdir(t);
        end

        % check if the file exists
        fname = fullfile(src_dir, int2str(fid), sprintf('DCX%d0001.mat', k));
        if ~exist(fname, 'file')
            continue;
        end
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
        m=matfile(fullfile(t, sprintf('DCX%d0001.mat', k)), 'writable', true);
        m.bm = bm;
    end
end
