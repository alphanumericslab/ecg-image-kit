function y = tanh_sat(x, param, varargin)
% tanh_sat - Saturates outlier samples using a tanh shape function
%
% Usage:
%   y = tanh_sat(x, param, mode)
% Inputs:
%   x: Input data, can be a vector or a matrix (channels x time)
%   param: Scaling factor for the saturation level:
%       - If mode == 'ksigma' or no mode defined: k times the standard deviation of each channel
%       - If mode = 'absolute': a vector of absolute thresholds used to
%           saturate each channel. If param is a scalar, the same value is
%           used for all channels
%   mode (optional): 'ksigma' or 'absolute'. Default is 'ksigma'
%
% Output:
%   y: Saturated data with outliers replaced by the saturation level
%
% Revision History:
%   2020: First release
%   2023: Renamed from deprecated version TanhSaturation()
%
% References:
%   Reza Sameni, 2020-2023
%   The Open-Source Electrophysiological Toolbox
%   https://github.com/alphanumericslab/OSET

if nargin > 2 && ~isempty(varargin{1})
    mode = varargin{1};
else
    mode = 'ksigma';
end

switch mode
    case 'ksigma'
        alpha = param * std(x, [], 2); % Compute the scaling factor based on the standard deviation of each channel
    case 'absolute'
        if isscalar(param)
            alpha = param * ones(1, size(x, 1));
        elseif isvector(param)
            if length(param) == size(x, 1)
                alpha = param;
            else
                error('Parameter must be a scalar or a vector with the same number of elements as the data channels');
            end
        end
    otherwise
        error('Undefined mode');
end

alpha = alpha(:); % Convert to a column vector
y = diag(alpha) * tanh(diag(1./alpha) * x); % Scale the input data and apply the tanh function to saturate outliers
