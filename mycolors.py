

from PIL import Image, ImageDraw, ImageColor, ImageFilter
import numpy as np
import skimage
import pandas as pd
from skimage import morphology

theta = np.sqrt(5) / 2 - 0.5

satVals = [
    (1.0, 1.0)
    ,(0.7, 0.5)
    ,(0.5, 1.0)
    ,(1.0, 0.7)
    ,(0.5, 0.5)
    ,(0.7, 1.0)
    ,(1.0, 0.5)
    ,(0.5, 0.7)
]



def mask(im, mask):
    ret = im.copy()
    ret[~mask] = (0, 0, 0)
    return ret


def rgb2hsv(im):
    if isinstance(im, tuple):
        return tuple(skimage.color.rgb2hsv([[np.array(im) / 255]])[0][0])
    else:
        return skimage.color.rgb2hsv(im)

def adjustSaturation(color, delta):
    hue, saturation, value = rgb2hsv(color)
    saturation += delta * saturation * (1 - saturation)
    return hsv2rgb((hue, saturation, value))

def adjustValue(color, delta):
    hue, saturation, value = rgb2hsv(color)
    value += delta * value * (1 - value)
    return hsv2rgb((hue, saturation, value))


def genMonoChroma(hue):
    return [(hue, i, j) for (i, j) in satVals]

def showMask(ar):
    display(Image.fromarray(ar))

def showAr(ar):
    display(Image.fromarray(ar))

def show(ar, factor = 255):
    display(Image.fromarray((ar * factor).astype('uint8')))
    

def plotValues(ar):
    pd.DataFrame(ar.flatten())[0].value_counts().sort_index().plot()

def hsv2rgb(hsv):
    return tuple((255 * skimage.color.hsv2rgb([[hsv]])).astype('uint8')[0][0])

hsv2rgb([0, 1.0, 1])

def genHueMask(im, a, b):
    if b > a:
        return (im[:,:,0] >= a) & (im[:,:,0] < b)
    else:
        return (im[:,:,0] < b) | (im[:,:,0] >= a)

def genSaturationMask(im, a, b):
    return (im[:,:,1] >= a) & (im[:,:,1] <= b)

def genValueMask(im, a, b):
    return (im[:,:,2] >= a) & (im[:,:,2] <= b)



def genSwapHue(t1, t2):
    def swapHue(h):
        l1 = t2 - t1
        l2 = 1 - l1
        if h < t1:
            ret = t1 - (h - t1) / l2 * l1
        elif h > t2:
            ret = t2 - (h - t2) / l2 * l1
        else:
            ret = t2 - (h - t2) / l1 * l2
        return ret
    return swapHue

def insideUnitPoint(x):
    return (x[0] >= 0) & (x[0] <= 1) & (x[1] >= 0) & (x[1] <= 1)

def insideUnitRegion(r):
    ret = False
    for v in r:
        if insideUnitPoint(v):
            ret = True
            break
    return(ret)
        

def myTrans(points):
    ret = []
    for point in points:
        pointRet = point.copy()
        for pointOther in points:
            pointRet += (pointOther - point) / 2 * myFact(point, pointOther)
        ret.append(pointRet)
    return ret

def myTransPass(points):
    return points

def myFact(point_1, point_2):
    return myFact_a ** 4 / (myFact_a ** 4 + (point_1[0] - point_2[0]) ** 4 + (point_1[1] - point_2[1]) ** 4)

def orderCenter(v):
    z = v[0] - 0.5 + 1j * (v[1] - 0.5)
    return abs(z) 

def orderPoint(v):
    z = v[0] - 0.5 + 1j * (v[1] - 0.5)
    return int(np.sqrt(abs(z)) * 40) + abs(np.log(z).imag) / (2 * np.pi)


def hsvText(hue=0, saturation=1, value=1):
    return(f"hsv({int(hue*360)},{int(saturation * 100)}%,{int(value*100)}%)")

hsvText(hue=0.3)

def drawPoint(point, color = "white"):
    center = point * width
    corner_1 = center - pointRadius
    corner_2 = center + pointRadius
    draw.ellipse(list(corner_1) + list(corner_2), fill = color)
    return corner_1, center

def drawLine(point_1, point_2, color = "white"):
    corner_1 = point_1 * width
    corner_2 = point_2 * width  
    draw.line(list(corner_1) + list(corner_2), fill = color, width = 3)
    
def drawPoints(points, color = "white"):
    [drawPoint(point, color) for point in points]

def drawChain(points, color = "white"):
    [drawLine(points[i], points[i + 1], color) for i in range(len(points) - 1)]
    

def genPoint(i):
    x = 0.5 + 0.5 * np.cos(i * mycolors.theta * np.pi * 2) * np.sqrt(i) / 40
    y = 0.5 + 0.5 * np.sin(i * mycolors.theta * np.pi * 2) * np.sqrt(i) / 40
    return np.array([x, y])

def colorMask(background, mask):
    return ImageStat.Stat(background, mask).median


def genMask(region):
    ret = Image.new(size=(width, height), mode="1")
    draw = ImageDraw.Draw(ret)
    testVertices = [tuple((vertices[v] * width).astype(int)) for v in region]
    draw.polygon(testVertices, fill=1)
    return ret