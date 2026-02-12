"""
Similarity functions for vector operations
These functions are used to measure how similar two vectors are
Understanding these is crucial for RAG - they determine which 
documents are "most relevant" to a query
"""
import numpy as np
from numpy.typing import NDArray

"""
Calculate the cosine similarity between two vectors
Cosine similarity measures the angle between two vectors, ignoring magnitude
A value of 1 means identical direction, 0 means orthogonal, -1 means opposite
Formula: cos(θ) = (A · B) / (||A|| × ||B||)
Args:
    vec_a: First vector (1D numpy array)
    vec_b: Second vector (1D numpy array)
Returns:
    Cosine similarity score between -1 and 1
Example:
    >>> import numpy as np
    >>> a = np.array([1, 0, 0])
    >>> b = np.array([1, 0, 0])
    >>> cosine_similarity(a, b)
    1.0
    >>> c = np.array([0, 1, 0])
    >>> cosine_similarity(a, c)
    0.0
"""
def cosine_similarity(
    vec_a: NDArray[np.float32],
    vec_b: NDArray[np.float32]
) -> float:
    """
    Calculate dot product: sum of element-wise multiplication
    """
    dot_product = np.dot(vec_a, vec_b)
    
    """
    Calculate magnitudes (L2 norms)
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    """
    Handle zero vectors to avoid division by zero
    """
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    """
    Calculate cosine similarity
    """
    similarity = dot_product / (norm_a * norm_b)
    
    """
    Clamp to [-1, 1] to handle floating point errors
    """
    return float(np.clip(similarity, -1.0, 1.0))

"""
Calculate the Euclidean distance between two vectors
Euclidean distance is the straight-line distance in N-dimensional space
Lower values mean more similar vectors
Formula: d = √(Σ(a_i - b_i)²)
Args:
    vec_a: First vector (1D numpy array)
    vec_b: Second vector (1D numpy array)
Returns:
    Euclidean distance (0 or positive)

Example:
    >>> import numpy as np
    >>> a = np.array([0, 0])
    >>> b = np.array([3, 4])
    >>> euclidean_distance(a, b)
    5.0
"""
def euclidean_distance(
    vec_a: NDArray[np.float32],
    vec_b: NDArray[np.float32]
) -> float:
    return float(np.linalg.norm(vec_a - vec_b))

"""
Calculate the dot product between two vectors
The dot product is the sum of element-wise multiplication
Higher values generally indicate more similarity for normalized vectors
Args:
    vec_a: First vector (1D numpy array)
    vec_b: Second vector (1D numpy array)
Returns:
    Dot product value
Example:
    >>> import numpy as np
    >>> a = np.array([1, 2])
    >>> b = np.array([3, 4])
    >>> dot_product(a, b)
    11.0
"""
def dot_product(
    vec_a: NDArray[np.float32],
    vec_b: NDArray[np.float32]
) -> float:
    return float(np.dot(vec_a, vec_b))
