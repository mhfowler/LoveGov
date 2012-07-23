########################################################################################################################
########################################################################################################################
#
#           Process
#
#
########################################################################################################################
########################################################################################################################

# python
import subprocess
import Image
import random

# lovegov
from lovegov.modernpolitics.initialize import *

#-----------------------------------------------------------------------------------------------------------------------
# This function takes an input a URL, snaps a screenshot image, saves that image to a temp directory, and outputs
# the url for the image on the server.
# TODO: clear temp directory.  Make resizing algorithm better.
# args: url - url to grab screenshot from
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def phantomJS(url):
    """
    This is to call phantomJS on a url and take an image snapshot of a website.

    @param url: the url of the website
    @type url: string
    """
    randomNumber = str(random.randint(0,1000000000000))
    relativePath = 'images/temp/' + randomNumber + '.png'
    imagePath = os.path.join(settings.MEDIA_ROOT, relativePath)
    subprocess.call([PHANTOMJS, PHANTOMJS_RASTERIZE, url, imagePath])
    image = Image.open(imagePath)
    if image.size[1] > 600:
        height = 600
    else:
        height = image.size[1]
    cropBox = (0, 0,image.size[0],height)
    image = image.crop(cropBox)
    image = image.resize((235, 180), Image.ANTIALIAS)
    image.save(imagePath)
    return os.path.join(settings.MEDIA_URL, relativePath)

