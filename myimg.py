
import numpy as np
import scipy
from PIL import Image

from scipy.cluster.vq import vq, kmeans, whiten

def imClustered(im, i):
    ar = np.array(im)
    ret = Image.fromarray(arClustered(ar, i))
    return ret

def arClustered(ar, i):
    shape = ar.shape
    colorData = ar.reshape((int(ar.size / 3), 3))
    codebook, distortion = kmeans(colorData.astype('float'), i) 
    code2color = lambda x: codebook.astype('uint8')[x]
    dataClustered, foo = vq(colorData, codebook)
    bar = np.apply_along_axis(code2color, 0, dataClustered)
    return bar.reshape(shape)

def detectEdges(ar, masks):
    edges = np.zeros(ar.shape)
    for mask in masks:
        edges = np.maximum(scipy.ndimage.convolve(ar, mask), edges)
    return edges.astype(int)

Faler=[ [[-1,0,1],[-1,0,1],[-1,0,1]], 
        [[1,1,1],[0,0,0],[-1,-1,-1]],
    [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]],
    [[0,1,0],[-1,0,1],[0,-1,0]] ]