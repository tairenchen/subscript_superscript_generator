# import numpy as np
# from scipy import stats
# import matplotlib.pyplot as plt

# def sample_font_size(min_size=5, max_size=60, peak=11.5, concentration=1.5, num_samples=1):
#     """
#     Sample font sizes based on a truncated normal distribution.
    
#     Parameters:
#     -----------
#     min_size : int
#         Minimum font size (inclusive)
#     max_size : int
#         Maximum font size (inclusive)
#     peak : float
#         Center of the distribution (where highest probability occurs)
#     concentration : float
#         Controls how concentrated values are around the peak (smaller = more concentrated)
#     num_samples : int
#         Number of samples to return
    
#     Returns:
#     --------
#     int or ndarray
#         Random font size(s) between min_size and max_size
#     """
#     # Create a truncated normal distribution
#     a = (min_size - peak) / concentration
#     b = (max_size - peak) / concentration
#     distribution = stats.truncnorm(a, b, loc=peak, scale=concentration)
    
#     # Sample from the distribution
#     samples = distribution.rvs(size=num_samples)
    
#     # Round to integers (for font sizes)
#     rounded_samples = np.round(samples).astype(int)
    
#     # Return either a single value or array depending on num_samples
#     if num_samples == 1:
#         return rounded_samples[0]
#     return rounded_samples

# # Example usage
# if __name__ == "__main__":
#     # Generate a single random font size
#     random_size = sample_font_size()
#     print(f"Random font size: {random_size}")
    
#     # Generate 1000 samples to visualize the distribution
#     samples = sample_font_size(num_samples=10000)
    
#     # Plot histogram to visualize the distribution
#     plt.figure(figsize=(10, 6))
#     bins = np.arange(4.5, 21.5, 1)  # Create bins centered on integers
#     plt.hist(samples, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
#     plt.xticks(range(5, 61))
#     plt.title('Font Size Distribution')
#     plt.xlabel('Font Size')
#     plt.ylabel('Frequency')
#     plt.grid(axis='y', alpha=0.3)
    
#     # Add vertical lines indicating the preferred range
#     plt.axvline(x=8, color='green', linestyle='--', alpha=0.5)
#     plt.axvline(x=14, color='green', linestyle='--', alpha=0.5)
    
#     # Highlight the peak
#     plt.axvline(x=11, color='red', linestyle='--', alpha=0.5)
#     plt.axvline(x=12, color='red', linestyle='--', alpha=0.5)
    
#     plt.tight_layout()
#     plt.savefig('font_size_distribution.png')
#     plt.show()

###------------------------------------------------
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def sample_font_size(min_size=5, max_size=60, peak=11.5, concentration=3.0, num_samples=1):
    """
    Sample font sizes based on a truncated normal distribution.
    
    Parameters:
    -----------
    min_size : int
        Minimum font size (inclusive)
    max_size : int
        Maximum font size (inclusive)
    peak : float
        Center of the distribution (where highest probability occurs)
    concentration : float
        Controls how concentrated values are around the peak (smaller = more concentrated)
    num_samples : int
        Number of samples to return
    
    Returns:
    --------
    int or ndarray
        Random font size(s) between min_size and max_size
    """
    # Create a truncated normal distribution
    a = (min_size - peak) / concentration
    b = (max_size - peak) / concentration
    distribution = stats.truncnorm(a, b, loc=peak, scale=concentration)
    
    # Sample from the distribution
    samples = distribution.rvs(size=num_samples)
    
    # Round to integers (for font sizes)
    rounded_samples = np.round(samples).astype(int)
    
    # Return either a single value or array depending on num_samples
    if num_samples == 1:
        return rounded_samples[0]
    return rounded_samples

def sample_font_size_mixture(min_size=5, max_size=60, num_samples=1):
    """
    Sample font sizes using a mixture of two truncated normal distributions.
    One focused on the 8-14 range and another allowing for larger sizes.
    """
    # First distribution focused on 8-14 range
    peak1 = 11.5
    concentration1 = 1.5
    a1 = (min_size - peak1) / concentration1
    b1 = (max_size - peak1) / concentration1
    dist1 = stats.truncnorm(a1, b1, loc=peak1, scale=concentration1)
    
    # Second distribution allowing for larger sizes
    peak2 = 25
    concentration2 = 10
    a2 = (min_size - peak2) / concentration2
    b2 = (max_size - peak2) / concentration2
    dist2 = stats.truncnorm(a2, b2, loc=peak2, scale=concentration2)
    
    # Mix the distributions (80% from first, 20% from second)
    mixture_weights = [0.8, 0.2]
    
    # Determine how many samples to take from each distribution
    n1 = int(mixture_weights[0] * num_samples)
    n2 = num_samples - n1
    
    # Sample from both distributions
    samples1 = dist1.rvs(size=n1)
    samples2 = dist2.rvs(size=n2)
    
    # Combine samples
    samples = np.concatenate([samples1, samples2])
    
    # Shuffle to mix them
    np.random.shuffle(samples)
    
    # Round to integers
    rounded_samples = np.round(samples).astype(int)
    
    if num_samples == 1:
        return rounded_samples[0]
    return rounded_samples
# # Example usage
if __name__ == "__main__":
    # Generate 10000 samples to visualize the distribution
    # samples = sample_font_size(min_size=2, max_size=10, peak=5.5, concentration=5.0, num_samples=100000)

    samples = sample_font_size_mixture(min_size=5, max_size=60, num_samples=100000)

    # Plot histogram to visualize the distribution
    plt.figure(figsize=(12, 6))
    bins = np.arange(0.5, 81.5, 1)  # Create bins centered on integers
    plt.hist(samples, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xticks(range(1, 81, 5))  # Show ticks every 5 units for readability
    plt.title('Font Size Distribution (5-60)')
    plt.xlabel('Font Size')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.3)

    # Add vertical lines indicating the preferred range
    plt.axvline(x=8, color='green', linestyle='--', alpha=0.5)
    plt.axvline(x=14, color='green', linestyle='--', alpha=0.5)

    # Highlight the peak
    plt.axvline(x=11, color='red', linestyle='--', alpha=0.5)
    plt.axvline(x=12, color='red', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('font_size_distribution_extended.png')
    plt.show()

