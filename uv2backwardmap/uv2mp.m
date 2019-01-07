function invmap = uv2mp(uv)
%uv2mp - Convert uv map to inverse map
%
% Syntax: invmap = uv2mp(uv)
%
% uv is a k*k*3 mat, the 3rd dim only provide the info for the mask of uv
% the first dim is u and second dim is v

% s is the size of output map
s = 448;
% rescale the 1.0 in uv to s which is the size of the output map
uv = uv * s;
sx = uv(:, :, 1);
sy = uv(:, :, 2);
% valid point
msk = uv(:, :, 3) > 0.1;
% sx sy are the value in the forward mapping but the coord in the backward mapping
sx = sx(msk);
sy = sy(msk);
% tx ty are the coord in the forward mapping but the value in the backward mapping
[ty, tx] = find(msk);
Fx = scatteredInterpolant(double(sx), double(sy), tx);
Fy = scatteredInterpolant(double(sx), double(sy), ty);
% sampling coord on the output mapping
[xq, yq] = meshgrid(1 : s, 1 : s);
% get the value based on the scattered interpolation
vx = Fx(xq, yq);
vy = Fy(xq, yq);
% concatenate togethetr
invmap = cat(3, vx, vy);
end