import os
import cv2
import numpy as np
import argparse
import math
from PIL import Image
import torch

def median_scaling(predicted_depth, ground_truth_depth, camera='BDE', fov=None, offset=None):
    """
    Perform median scaling to adjust the predicted depth based on the ground truth depth.

    :param predicted_depth: The predicted depth map.
    :param ground_truth_depth: The ground truth depth map.
    :param error_type: Type of scaling ('MDE' or 'BDE'). Defaults to 'BDE'.
    :param fov: Field of view in degrees (required for 'BDE').
    :param offset: A scaling offset (required for 'BDE').
    :return: Adjusted predicted depth, scale factor, and mask.
    """
    predicted_depth = resize_image(np.squeeze(predicted_depth), ground_truth_depth)
    
    if camera == 'BDE':
        # Only apply fov and offset for BDE
        fov_dep = calculate_focal_length(fov, ground_truth_depth.shape[1])
        predicted_depth = calculate_depth(fov_dep, offset * 2, predicted_depth)
    
    # Create mask where ground truth depth is greater than 30
    mask = ground_truth_depth <= 30  # Mask where True indicates depth <= 30
    masked_gt = ground_truth_depth * mask  # Apply mask to ground truth
    masked_pred = predicted_depth * mask  # Apply mask to predicted depth

    # Calculate median values for valid (non-zero) depths
    valid_gt = masked_gt[masked_gt > 0]  # Only consider non-zero ground truth
    valid_pred = masked_pred[masked_pred > 0]  # Only consider non-zero predicted

    median_gt = np.median(valid_gt)  # Median of ground truth depth
    median_pred = np.median(valid_pred)  # Median of predicted depth

    # Compute scaling factor
    scale_factor = median_gt / median_pred

    # Apply scaling factor to predicted depth
    metric_depth = masked_pred * scale_factor

    return metric_depth, scale_factor, mask


def process_depth_array(depth_array):
    """
    Process depth array by setting values greater than 30 to 0.
    
    :param depth_array: Depth array to process.
    :return: Processed depth array.
    """
    depth_array[depth_array > 30] = 0
    return depth_array


def read_image(file_path):
    """
    Read depth image from the given file path based on file extension.

    :param file_path: The file path of the depth image.
    :return: Depth data read from the image.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.npy':
        depth_data = np.load(file_path)
    elif file_extension == '.png':
        depth_data = np.array(Image.open(file_path))
    elif file_extension == '.jpeg':
        depth_data = np.array(Image.open(file_path))
    elif file_extension == '.pfm':
        depth_data = read_pfm(file_path)
    
    return depth_data


def resize_image(depth_data, gt_data):
    """
    Resize depth data to match the size of ground truth data.

    :param depth_data: The predicted depth data to resize.
    :param gt_data: The ground truth depth data for reference.
    :return: Resized depth data.
    """
    resized_data = cv2.resize(depth_data, (gt_data.shape[1], gt_data.shape[0]))
    return resized_data


def read_pfm(file_path):
    """
    Read depth data from a PFM file.

    :param file_path: The path to the PFM file.
    :return: Depth data read from the PFM file.
    """
    with open(file_path, 'rb') as file:
        header = file.readline().decode('utf-8').rstrip()
        color = header == 'PF'

        width, height = map(int, file.readline().decode('utf-8').split())
        scale = float(file.readline().decode('utf-8').rstrip())
        endian = '<' if scale < 0 else '>'

        depth_data = np.fromfile(file, endian + 'f')
        depth_data = np.reshape(depth_data, (height, width, 3) if color else (height, width))

        # Flip the depth data upside down
        depth_data = np.flipud(depth_data)

    return depth_data


def calculate_focal_length(fov_deg, img_width):
    """
    Calculate the focal length in pixels.

    :param fov_deg: Field of view in degrees.
    :param img_width: Image width in pixels.
    :return: Focal length in pixels.
    """
    fov_rad = math.radians(fov_deg)
    f = img_width / (2 * math.tan(fov_rad / 2))
    return f


def calculate_depth(f, B, d):
    """
    Calculate depth based on the formula z = (f * B) / d.

    :param f: Focal length in pixels.
    :param B: Baseline in pixels.
    :param d: Disparity in pixels.
    :return: Depth in pixels or millimeters.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        z = (f * B) / d
    return z


def compute_metrics(gt, pred):
    """
    Compute depth estimation metrics.

    :param gt: Ground truth depth map.
    :param pred: Predicted depth map.
    :return: Depth estimation metrics.
    """
    valid_mask = (gt > 0) & (pred > 0)

    abs_rel = np.mean(np.abs(gt[valid_mask] - pred[valid_mask]) / gt[valid_mask])
    sq_rel = np.mean(((gt[valid_mask] - pred[valid_mask]) ** 2) / gt[valid_mask])
    rmse = np.sqrt(np.mean((gt[valid_mask] - pred[valid_mask]) ** 2))
    
    rmse_log = np.sqrt(np.mean((np.log(gt[valid_mask]) - np.log(pred[valid_mask])) ** 2)) if valid_mask.any() else float('nan')

    thresh = np.maximum((gt[valid_mask] / pred[valid_mask]), (pred[valid_mask] / gt[valid_mask]))
    delta1 = np.mean(thresh < 1.25)
    delta2 = np.mean(thresh < 1.25 ** 2)
    delta3 = np.mean(thresh < 1.25 ** 3)

    log_gt = np.log(gt + 1e-10)
    log_pred = np.log(pred + 1e-10)
    err_log = log_gt[valid_mask] - log_pred[valid_mask]
    normalized_squared_log = np.mean(err_log**2)
    log_mean = np.mean(err_log)
    silog_error = math.sqrt(normalized_squared_log - log_mean**2) * 100

    return abs_rel, sq_rel, rmse, rmse_log, delta1, delta2, delta3, silog_error


def process_depth_data(file_path):
    """
    Process depth data by reading different file types: .npy, .png, .jpeg, .pfm.

    :param file_path: The file path of the depth image.
    :return: The depth data read from the file.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.npy':
        depth_data = np.load(file_path)
    elif file_extension == '.png':
        depth_data = np.array(Image.open(file_path))
    elif file_extension == '.jpeg':
        depth_data = np.array(Image.open(file_path))
    elif file_extension == '.pfm':
        depth_data = read_pfm(file_path)

    return depth_data


if __name__ == "__main__":
    # Example of how to use the above functions with command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--pre', required=True, help="Path to the predicted depth image")  # Changed from '--rgb'
    parser.add_argument('--gt', required=True, help="Path to the ground truth depth image")  # Changed from '--depth'
    parser.add_argument('--camera', choices=['MDE', 'BDE'], required=True, help="Camera type: 'MDE' or 'BDE'. ")
    parser.add_argument('--fov', type=float, default=90, help="Field of View (default is 90 degrees)")
    parser.add_argument('--offset', type=float, default=0.5, help="Baseline (only BDE)")
    args = parser.parse_args()

    # Load depth data
    predicted_depth = process_depth_data(args.pre)  # Changed from args.depth to args.pre
    ground_truth_depth = np.load(args.gt)  # Changed from args.rgb to args.gt

    # Perform median scaling
    if args.camera == 'MDE':
        metric_depth, scale_factor, mask = median_scaling(predicted_depth, ground_truth_depth, camera='MDE')
    else:
        metric_depth, scale_factor, mask = median_scaling(predicted_depth, ground_truth_depth, camera='BDE', fov=args.fov, offset=args.offset)
    
    metric_depth = process_depth_array(metric_depth)

    # Compute and print metrics
    metrics = compute_metrics(ground_truth_depth, metric_depth)
    metric_names = ["AbsRel", "SqRel", "RMSE", "RMSE_Log", "Delta_1", "Delta_2", "Delta_3", "SILog"]
    
    for name, value in zip(metric_names, metrics):
        print(f"{name}: {value:.6f}")


