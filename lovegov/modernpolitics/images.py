########################################################################################################################
########################################################################################################################
#
#           Images
#
#
########################################################################################################################
########################################################################################################################

# django
from django.conf import settings

# python
import random
import os
import urllib
import Image
import urlparse
from StringIO import StringIO

def downloadImage(img_url,url,min_size=40000):
    def saveImage(img_url,min_size,relativePath="images/temp/"):
        """
        Takes a URL for an image, downloads 2kb, check dimensions of image, if dimension are large enough
        then save full image to temp path in media directory with random integer.

        PYTHON PIL IMAGES DOES NOT SUPPORT ANIMATEF GIFS

        @param img_url: the url for an image file
        @type img_url: string
        @param min_size: minimum height/width of an image in order to download
        @type min_siz: integer
        @param relativePath: relative path in which to save the image file
        @return dictionary
        """
        try:
            relativePath += str(random.randint(0,1000000000000))                        # get random filepath/filename
            if ".png" in img_url: relativePath += '.png'                                #
            elif ".jpg" in img_url: relativePath += '.jpg'                              #  switch for image
            elif ".jpeg" in img_url: relativePath += '.jpeg'                            #  types
            else: return False
            imagePath = os.path.join(settings.MEDIA_ROOT, relativePath)                 # to put image in correct media folder
            image_on_web = urllib.urlopen(img_url)                                      # GET request for image from url
            partialImgBytes = StringIO(image_on_web.read(10000))                         # read first 2048 bytes
            partialImg = Image.open(partialImgBytes)                                    # open partial image from bytes
            size = partialImg.size[0]  * partialImg.size[1]                             # get size metadata from partial image
            if size > min_size:                                                         # check if image is big enough to be useful
                downloaded_image = file(imagePath, "wb")                                # open new binary file with intent to write
                image_on_web = urllib.urlopen(img_url)                                  # new GET request for image
                downloaded_image.write(image_on_web.read())                             # read full number of bytes this time
                try:
                    check = file(imagePath,'rb')                                        # check if image can indeed be opened
                    Image.open(check)
                except IOError: return False
                downloaded_image.close()                                                # close streams
                image_on_web.close()                                                    # close streams
                return {'path':imagePath,'size':size}                                   # return path to image and its size
            else:
                return False
        except:
            return False

    if img_url.startswith('/'):
        hostname = 'http://' + urlparse.urlparse(url).hostname
        imageObj = saveImage(img_url=str(hostname + img_url),min_size=min_size)
    elif img_url.startswith("http://"):
        imageObj = saveImage(img_url=img_url,min_size=min_size)
    else:
        imageObj = saveImage(img_url=str(url + img_url),min_size=min_size)
    return imageObj

#-----------------------------------------------------------------------------------------------------------------------
# resize an image.
#-----------------------------------------------------------------------------------------------------------------------
def resizeImage(img_path,basewidth=230,maxheight=230):
    try:
        img = Image.open(img_path)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize),Image.ANTIALIAS)
        if img.size[1] > maxheight: img = img.crop((0,0,img.size[0],maxheight))
        img.save(img_path)
        return str(img_path).replace(settings.MEDIA_ROOT,settings.MEDIA_URL)
    except:
        pass