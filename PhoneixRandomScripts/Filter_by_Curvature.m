% Usamah Chaudhary, Sophia Simms, Connor Hazen
% restor3d/protect3d Duke Project Phoenix 

clear all; clc;
close all;

%% Reading in Input (Fixed)
file = '/Users/Sophia/protect3d-restor3d-Phoenix/MATLAB/ankle_scans/AnkleMesh_1_L_Input.stl';

A = stlread(file);
B = A.Points;
ptcld = pointCloud(B);

% downsample 
%if ptcld.Count > 1500
%    scale_factor = 1500/ptcld.Count;
%    ptcld = pcdownsample(ptcld,'random', scale_factor);
%end

%% find normals and curvature
[normals,curvature] = findPointNormals(ptcld.Location,[],[0,0,0],true);

% map of orginal ptcld based on normals
figure();
scatter3(ptcld.Location(:, 1), ptcld.Location(:,2), ptcld.Location(:,3), [], normals(:,1),'filled') 
caxis([min(normals(:,1)) max(normals(:,1))]); % color overlay the direction of normals
title('Original');
colormap jet;
colorbar;
legend('Original')
hold on;
quiver3(ptcld.Location(:,1),ptcld.Location(:,2),ptcld.Location(:,3),...  
    normals(:,1),normals(:,2),normals(:,3), 'r'); % show normal vectors
axis equal;

%% filter unwanted pts 

% to keep only regions of high curvature, remove points within chosen range
upper = 0.8;
lower = -0.8;

idx = find(normals(:,1) <= upper & normals(:,1) >= lower); % indices of unwanted pts
idx2 = find(normals(:,1) >= upper | normals(:,1) <= lower); % indices of wanted pts
normals(idx) = NaN; % remove from normals array
ptcldDelete = select(ptcld, idx); 
ptcld2 = select(ptcld,idx2);

%cluster
minDistance = 15;
[labels,numClusters] = pcsegdist(ptcld2,minDistance);
figure();
scatter3(ptcld2.Location(:, 1), ptcld2.Location(:,2), ptcld2.Location(:,3), [], labels,'filled')
colormap(hsv(numClusters));
title('Clusters');

idxCluster = find(labels == 1);
ptcldCluster = select(ptcld2,idxCluster);
figure();
scatter3(ptcldCluster.Location(:, 1), ptcldCluster.Location(:,2), ptcldCluster.Location(:,3), 'filled')
title('Largest Cluster');

% fill in pts by applying limits of wanted cluster to original ptcld

X = ptcldCluster.XLimits;
Y = ptcldCluster.YLimits;
Z = ptcldCluster.ZLimits;
roi = [X Y Z];
idxFinal = findPointsInROI(ptcld,roi);
ptcldFinal = select(ptcld, idxFinal);

figure();
scatter3(ptcldFinal.Location(:, 1), ptcldFinal.Location(:,2), ptcldFinal.Location(:,3), 'filled') 
title('Original with Bounding Box');

%% main plot
hold off;

% map of orginal ptcld based on normals, post-filtering
figure();
scatter3(ptcld.Location(:, 1), ptcld.Location(:,2), ptcld.Location(:,3), [], normals(:,1),'filled') 
caxis([min(normals(:,1)) max(normals(:,1))]); % color overlay the direction of normals
title('Direction of normals');
colormap jet;
colorbar;
legend('Original')
hold on;
quiver3(ptcld.Location(:,1),ptcld.Location(:,2),ptcld.Location(:,3),...  
    normals(:,1),normals(:,2),normals(:,3), 'r'); % show normal vectors
axis equal;

%%
function [ normals, curvature ] = findPointNormals(points, numNeighbours, viewPoint, dirLargest)
%FINDPOINTNORMALS Estimates the normals of a sparse set of n 3d points by
% using a set of the closest neighbours to approximate a plane.
%
%   Required Inputs:
%   points- nx3 set of 3d points (x,y,z)
%
%   Optional Inputs: (will give default values on empty array [])
%   numNeighbours- number of neighbouring points to use in plane fitting
%       (default 9)
%   viewPoint- location all normals will point towards (default [0,0,0])
%   dirLargest- use only the largest component of the normal in determining
%       its direction wrt the viewPoint (generally provides a more stable
%       estimation of planes near the viewPoint, default true)
%
%   Outputs:
%   normals- nx3 set of normals (nx,ny,nz)
%   curvature- nx1 set giving the curvature
%
%   References-
%   The implementation closely follows the method given at
%   http://pointclouds.org/documentation/tutorials/normal_estimation.php
%   This code was used in generating the results for the journal paper
%   Multi-modal sensor calibration using a gradient orientation measure 
%   http://www.zjtaylor.com/welcome/download_pdf?pdf=JFR2013.pdf
%
%   This code was written by Zachary Taylor
%   zacharyjeremytaylor@gmail.com
%   http://www.zjtaylor.com

%% check inputs
validateattributes(points, {'numeric'},{'ncols',3});

if(nargin < 2)
    numNeighbours = [];
end
if(isempty(numNeighbours))
    numNeighbours = 9;
else
    validateattributes(numNeighbours, {'numeric'},{'scalar','positive'});
    if(numNeighbours > 100)
        warning(['%i neighbouring points will be used in plane'...
            ' estimation, expect long run times, large ram usage and'...
            ' poor results near edges'],numNeighbours);
    end
end

if(nargin < 3)
    viewPoint = [];
end
if(isempty(viewPoint))
    viewPoint = [0,0,0];
else
    validateattributes(viewPoint, {'numeric'},{'size',[1,3]});
end

if(nargin < 4)
    dirLargest = [];
end
if(isempty(dirLargest))
    dirLargest = true;
else
    validateattributes(dirLargest, {'logical'},{'scalar'});
end

%% setup

%ensure inputs of correct type
points = double(points);
viewPoint = double(viewPoint);

%create kdtree
kdtreeobj = KDTreeSearcher(points,'distance','euclidean');

%get nearest neighbours
n = knnsearch(kdtreeobj,points,'k',(numNeighbours+1));

%remove self
n = n(:,2:end);

%find difference in position from neighbouring points
p = repmat(points(:,1:3),numNeighbours,1) - points(n(:),1:3);
p = reshape(p, size(points,1),numNeighbours,3);

%calculate values for covariance matrix
C = zeros(size(points,1),6);
C(:,1) = sum(p(:,:,1).*p(:,:,1),2);
C(:,2) = sum(p(:,:,1).*p(:,:,2),2);
C(:,3) = sum(p(:,:,1).*p(:,:,3),2);
C(:,4) = sum(p(:,:,2).*p(:,:,2),2);
C(:,5) = sum(p(:,:,2).*p(:,:,3),2);
C(:,6) = sum(p(:,:,3).*p(:,:,3),2);
C = C ./ numNeighbours;

%% normals and curvature calculation

normals = zeros(size(points));
curvature = zeros(size(points,1),1);
for i = 1:(size(points,1))
    
    %form covariance matrix
    Cmat = [C(i,1) C(i,2) C(i,3);...
        C(i,2) C(i,4) C(i,5);...
        C(i,3) C(i,5) C(i,6)];  
    
    %get eigen values and vectors
    [v,d] = eig(Cmat);
    d = diag(d);
    [lambda,k] = min(d);
    
    %store normals
    normals(i,:) = v(:,k)';
    
    %store curvature
    curvature(i) = lambda / sum(d);
end

%% flipping normals

%ensure normals point towards viewPoint
points = points - repmat(viewPoint,size(points,1),1);
if(dirLargest)
    [~,idx] = max(abs(normals),[],2);
    idx = (1:size(normals,1))' + (idx-1)*size(normals,1);
    dir = normals(idx).*points(idx) > 0;
else
    dir = sum(normals.*points,2) > 0;
end

normals(dir,:) = -normals(dir,:);

end