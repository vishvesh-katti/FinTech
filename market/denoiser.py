import numpy as np
import pandas as pd

def denoise_covariance_matrix(returns_matrix):
    """
    Implements Marchenko-Pastur covariance denoising.
    returns_matrix: np.ndarray of shape (T, N) where T = days, N = assets.
    """
    T, N = returns_matrix.shape
    if N == 0 or T == 0:
        return np.cov(returns_matrix, rowvar=False)
        
    Q = T / N
    
    # 1. Compute empirical correlation matrix C
    # Convert returns to correlation matrix
    cov_emp = np.cov(returns_matrix, rowvar=False)
    
    # Handle single asset case
    if N == 1:
        return cov_emp * 252.0
        
    std_dev = np.sqrt(np.diag(cov_emp))
    outer_std = np.outer(std_dev, std_dev)
    # Avoid division by zero
    outer_std[outer_std == 0] = 1e-10
    corr_emp = cov_emp / outer_std
    
    # 2. Eigendecompose
    eigenvalues, eigenvectors = np.linalg.eigh(corr_emp)
    
    # Sort eigenvalues and eigenvectors in descending order
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # 3. Marchenko-Pastur threshold
    sigma_sq = 1.0 # normalized
    lambda_max = sigma_sq * (1 + np.sqrt(1/Q))**2
    
    # 4. Replace noise eigenvalues with their mean
    noise_mask = eigenvalues <= lambda_max
    if np.any(noise_mask):
        noise_mean = np.mean(eigenvalues[noise_mask])
        eigenvalues[noise_mask] = noise_mean
        
    # 5. Reconstruct denoised correlation matrix
    Lambda = np.diag(eigenvalues)
    corr_denoised = eigenvectors @ Lambda @ eigenvectors.T
    
    # Ensure diagonal is 1
    np.fill_diagonal(corr_denoised, 1.0)
    
    # 6. Convert back to covariance matrix and annualize
    cov_denoised = corr_denoised * outer_std
    
    return cov_denoised * 252.0
