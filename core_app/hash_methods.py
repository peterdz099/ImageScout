import os
import cv2
import numpy as np
from PIL import Image
import imagehash


def calculate_hamming_distance(first_hash, second_hash):
    first_hash_bin = hash_hex_to_binary(first_hash)
    second_hash_bin = hash_hex_to_binary(second_hash)
    hamming_distance = 0
    if first_hash_bin and second_hash_bin:
        for i in range(len(first_hash_bin)):
            if first_hash_bin[i] != second_hash_bin[i]:
                hamming_distance += 1
    else:
        hamming_distance = -1
    return hamming_distance


def calculate_cosine_similarity(vector_a, vector_b):
    return np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))


def calculate_feature_vector(image_path, bins=32):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v = cv2.calcHist([image], [2], None, [bins], [0, 256])
    s = cv2.calcHist([image], [1], None, [bins], [0, 256])
    h = cv2.calcHist([image], [0], None, [bins], [0, 256])
    vector = np.concatenate([v, s, h], axis=0)
    vector = vector.reshape(-1)  # 2D to 1D
    return vector

def binary_to_hash_hex(binary_string):
    # convert binary_string hash string in hex
    return hex(int(binary_string, 2))


def hash_hex_to_binary(hash_hex):
    # convert hash array of 0 or 1 to hash string in hex
    return bin(int(hash_hex, 16))[2:]


def p_hash(image_path):

    image = cv2.imread(image_path)  # image loading

    image = cv2.resize(image, (8, 8))  # image resizing
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # converting image to grayscale

    imf = np.float32(grayscale)  # convert grayscale image matrix to floats

    dst = cv2.dct(imf, cv2.DCT_INVERSE)  # calculate Discrete Cosine Transform

    dst_88 = dst[:8, :8]

    numpy_array = np.array(dst_88) # convert 8x8 matrix to np array

    average = (dst_88.mean() * dst_88.size - dst_88[0, 0]) / (dst_88.size - 1)  # calculate average of dct 8x8

    # creating 64-bit image fingerprint
    binary_string = ''
    for row in numpy_array:
        for i in row:
            if i >= average:
                binary_string += '1'
            elif i < average:
                binary_string += '0'

    p_hash = binary_to_hash_hex(binary_string)  # convert binary fingerprint ti hexadecimal
    return p_hash
