from PIL import Image, ImageFilter, ImageSequence
from IPython.display import Image as showImage
import subprocess
import numpy as np
import os
import shutil
import jinja2 as jinja

templateLoader = jinja.FileSystemLoader(searchpath="./templates")
templateEnv = jinja.Environment(loader=templateLoader)

g = type("global", (), {})()
g.verbose = False

TEMP_FOLDER = "c:/work/temp/"
INPUT_FOLDER = "c:/work/input/" 
OUTPUT_FOLDER = 'c:/work/output/'
SDCARD_FOLDER = "d:/dcim/104CANON/"
HTML_FOLDER = "c:/work/html/"
imgType = "png"
maxFileSize = 1000000000
ffmpegPath = "C:/Users/jokemjaa/Downloads/ffmpeg/ffmpeg/bin/ffmpeg"

def tFormat(secondsAll):
    minutes = int(secondsAll / 60)
    seconds = secondsAll - 60 * minutes
    return f"{minutes:02d}:{seconds:02d}"
    
tFormat(742)

def clearTempFolder():
    filelist = [ f for f in os.listdir(TEMP_FOLDER) if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(TEMP_FOLDER, f))

def clearOutputFolder():
    filelist = [ f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".png") ]
    for f in filelist:
        os.remove(os.path.join(OUTPUT_FOLDER, f))
        
def copyFromSdCard():
    files = newSdCardMovies()
    for i, f in enumerate(files):
        print(f"Copying {i + 1}/{len(files)} {f}")
        shutil.copy(os.path.join(SDCARD_FOLDER, f), INPUT_FOLDER)
    

def extractFrames(videoName):
    """Extracts single frames from video in temp folder."""
    print(f"Extracting {videoName}...") 
    clearTempFolder()
    videoPath = (INPUT_FOLDER + videoName).replace('/', '\\')
    p = subprocess.Popen([
        ffmpegPath
        ,'-i', videoPath
#         ,'-ss', '02:00'
#         ,'-to', '02:20'
#         ,'-vf', 'fps=1'
        ,TEMP_FOLDER + "frame%04d." + imgType
        ,"-hide_banner"
    ], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, close_fds = True)
    output, err = p.communicate()
    rc = p.returncode
    ffmpegLog = f"rc = {rc}\noutput = {output}\nerr = {err}"
    if rc > 0:
        print("Extract Failed!")
        print(ffmpegLog)
    else:
        print("Extract Ok")

# extractFrames("c:/work/input/MVI_2016.avi")
        
def concatFrames(outFile):
# ffmpeg -r 1/5 -start_number 2 -i img%03d.png -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4
    output = OUTPUT_FOLDER + outFile
    print(f"Writing file {output}")
    p = subprocess.Popen([ffmpegPath
#                           ,'-r', '1/10'
                          ,'-i', 'c:\\work\\output\\frame%04d.png' 
#                           ,'-vf', 'fps=25'
#                           ,'-c:v', 'libx264'
#                           ,'-pix_fmt', 'yuv420p'
                          ,output], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print(f"Concat start  {output} ...")
    output, err = p.communicate()
    rc = p.returncode
    ffmpegLog = f"rc = {rc}\noutput = {output}\nerr = {err}"
    if rc > 0:
        print(ffmpegLog)
    else:
        print("Concat Ok")

        
def openHtmlPage(folderName, pageName):
    p = subprocess.Popen(["C:\Program Files (x86)\Google\Chrome\Application\chrome"
                      ,"-d", f"file:///C:/work/html/{folderName}/{pageName}.html"
                     ])

# extractFrames(videoFile)
# C:\Users\jokemjaa\Downloads\ffmpeg-20190705-a514244-win64-static\ffmpeg-20190705-a514244-win64-static\bin\ffmpeg -i "C:\Users\jokemjaa\OneDrive - Tieto Corporation\Notebooks/20190704_172945.mp4" c:\mytest.gif
# C:\Users\jokemjaa\Downloads\ffmpeg-20190705-a514244-win64-static\ffmpeg-20190705-a514244-win64-static\bin

# myFilter = ImageFilter.BoxBlur(1)
# myFilter = ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)

def generatePageFolder(pageName):
    try:
        os.mkdir('c:/work/html/' + pageName)
    except:
        print("Kansio jo olemassa")

def generatePage(folder, name, code):
    with open('c:/work/html/pageTemplate.html', 'r') as f:
        templateHtml = f.read()
    pageHtml = templateHtml.replace('<<<code>>>', code)
    pageName = f'c:/work/html/{folder}/{name}.html'
    with open(pageName, 'w') as f:
        f.write(pageHtml)
    return pageName

# generatePage('test', 'fuuga')

def sdCardMovies():
#     return [file for file in os.listdir(SDCARD_FOLDER) if "MOV" in file]
    ret = []
    with os.scandir(SDCARD_FOLDER) as dir_contents:
        for entry in dir_contents:
            if "MOV" in entry.name:
                info = entry.stat()
                if info.st_size < maxFileSize:
#                     print(f"{entry.name} {info.st_size}")
                    ret.append(entry.name)
    return ret

def newSdCardMovies():
    return [file for file in sdCardMovies() if not file in inputMovies()]

def inputMovies(filetype = "MOV"):
    return [file for file in os.listdir(INPUT_FOLDER) if filetype in file]

def HTML_FOLDERs():
    return [file for file in os.listdir(HTML_FOLDER)]

def iterMovie(filetype = "MOV"):
    """ Finds next movie that is not extracted in html folder"""
    ret = ''
    for name in reversed(inputMovies(filetype)):
        isOld = False
        for folderName in HTML_FOLDERs():
            if folderName in name:
                isOld = True
        if isOld:
            continue
        ret = name
    return ret

class TEMP_FOLDERImages():
    def __init__(self, choice):
        self.choice = choice
    def __enter__(self):
        self.ims = readTempFolderImages(self.choice)
        return self.ims
    def __exit__(self, type, value, traceback):
        for im in self.ims:
            im[0].close()

def readTempFolderImages(choice):
    """ Returns list of images in temp Folder """     
    ret = []
    for ind, file in enumerate(os.listdir(TEMP_FOLDER)):
        if ind in choice:
            imPath = os.path.join(TEMP_FOLDER, file)
            im = Image.open(imPath, mode = 'r')
            ret.append((im, file.replace(".", "_")))
    if g.verbose:
        print(f"Read {len(ret)} images in list")
    return ret


def aggregate(imlist, numpyAggFunc, wall = 0, skip = 1, *args, **kwargs):
    """ Returns aggregate image of a list of images """
#     images = np.array([np.array(i[0]) for i in imlist[wall:-(wall + 1):skip]])
    images = np.array([np.array(i[0]) for i in imlist])
    ret = numpyAggFunc(images, *args, **kwargs, axis = 0)
    return Image.fromarray(np.array(np.round(ret), dtype=np.uint8))


def tempMedian(choice):
    with TEMP_FOLDERImages(choice) as ims:
        kwargs = {'q' : 0.5}
        ret = aggregate(ims, np.quantile, **kwargs)
    return ret

from skimage.color import rgb2hsv


def getMask(im1, im2, atol, rtol):
#     hue_img1 = rgb2hsv(im1)
#     hue_img2 = rgb2hsv(im2)
#     npDiffAv = np.isclose(hue_img1, hue_img2, atol = atol, rtol = rtol)
    npDiffAv = np.isclose(im1, im2, atol = atol, rtol = rtol)
#     if g.verbose:
#         display(npDiffAv)
    return myMaskArray(npDiffAv)   

def getMaskImg(im1, im2, im3, atol, rtol):
    return Image.fromarray(im3 * getMask(im1, im2, atol, rtol))          

def myMask(b):
    if b:
        return 0
    else:
        return 1
    
def myMaskArray(arr):
    a = np.array(np.vectorize(myMask)(arr), dtype = np.uint8)
    b = a.max(axis = 2)
    a[:,:,0] = b
    a[:,:,1] = b
    a[:,:,2] = b
#     nyBlur = ImageFilter.BoxBlur(5)
#     imc = Image.fromarray(a)
#     if g.verbose:
#         display(imc)
#     imb = imc.filter(nyBlur)
#     threshold = 50  
#     imc = imb.point(lambda p: p > threshold and 255) 
#     ret = np.asarray(imc)
    return a


def sumCopies(choice, imMedian, copyCount, offset, atol, rtol):
    with TEMP_FOLDERImages(choice) as ims:
        imageCount = int(len(ims) / copyCount)
        mask = getMask(imMedian, imMedian, atol, rtol)
        maskCurs = []
        for i in range(copyCount):
            imCur = ims[offset + i * imageCount][0]
            maskCur = getMask(imMedian, imCur, atol, rtol)
            maskCurs.append(maskCur)
            mask = mask + maskCur - mask * maskCur 
        imMasked = (1 - mask) * imMedian
        for i in range(copyCount):
            maskCur = maskCurs[i]
            imCur = ims[offset + i * imageCount][0]
            imMasked = imMasked * (1 - maskCur) + maskCur * imCur
    return Image.fromarray(imMasked)

def avgCopies(choice, copyCount, offset, numpyAggFunc, *args, **kwargs):
    with TEMP_FOLDERImages(choice) as ims:
        imageCount = int(len(ims) / copyCount)
        retIms = [ims[offset + i * imageCount] for i in range(copyCount)]
        ret = aggregate(retIms, numpyAggFunc, *args, **kwargs)
    return ret


def generateAggregates(pageName, tests, choice, transpose = False):
    generatePageFolder(pageName)
    imagesHtml = ''
    with TEMP_FOLDERImages(choice) as ims:
        for name, fun, kwargs in tests:
            print(name)
            im = aggregate(ims, fun, **kwargs)
            fileName = name.replace('.', '').replace(' ', '')
            if transpose:
                im = im.transpose(Image.ROTATE_270)
            im.save(f"c:/work/html/{pageName}/{fileName}.png")
            iterHtml = f'<h2>{name}</h2><img src="{fileName}.png" alt="{name}">'
            imagesHtml += iterHtml
    generatePage(pageName, 'page', imagesHtml)
    openHtmlPage(pageName, 'page')
    
def generateThumbnailsOld(pageName, choice = [], factor = 0.25, transpose = False):
    print("Generating thumbnails...")
    generatePageFolder(pageName)
    imagesHtml = ''
    with TEMP_FOLDERImages(choice) as ims:
        width, height = ims[0][0].size
        for ind, im in enumerate(ims):
            fileName = im[1]
            tn = im[0].resize((int(width * factor), int(height * factor)))
            if transpose:
                tn = tn.transpose(Image.ROTATE_270)
            tn.save(f"c:/work/html/{pageName}/tn_{fileName}.png")
            iterHtml = f'<h2>Thumb {ind}, file name {fileName}, </h2><img src="tn_{fileName}.png" alt="{fileName}">'
            imagesHtml += iterHtml
    generatePage(pageName, 'thumbnails', imagesHtml)
    print("Generate ok")
    openHtmlPage(pageName, 'thumbnails')

def generateThumbnails(pageName, skip = 30):
    generatePageFolder(pageName)
    links = ['file:///' + os.path.join(TEMP_FOLDER, f) for f in os.listdir(TEMP_FOLDER)][::skip]
    template = templateEnv.get_template("devgallery.html")
    imagesHtml = template.render({'links' : links, 'headerInformation' : pageName})
    print(f"Generated : {generatePage(pageName, 'thumbnails', imagesHtml)}")
    openHtmlPage(pageName, 'thumbnails')
    
# ims[100]
# aggregate(ims[50:-50:10],  myStd)
# out = aggregate(ims, np.average, wall = 30, skip = 10)
# out = aggregate(ims, np.quantile, wall = 30, skip = 10, q = 0.9)
# myStd = lambda x, **kwargs: 4 * np.std(x, **kwargs)
# out = aggregate(ims, myStd, wall = 30, skip = 10)
# out