from lovegov.settings import PROJECT_PATH
from django.conf import settings
import os
import re

css = PROJECT_PATH + '/frontend/static/css'
compiled = css + '/compiled'
scss = css + '/scss'

from tempfile import mkstemp
from shutil import move
from os import remove, close

def replace(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
        #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file)
    #Move new file
    move(abs_path, file)

# modify static_url in master-variables
master_variables_file = scss + '/master-variables.scss'
old_static = "$STATIC_URL: '/static';"
new_static = "$STATIC_URL: '" + settings.STATIC_URL + "';"

replace(master_variables_file, old_static, new_static)

def compileFolder(relative_path):
    scss_files = os.listdir(scss + relative_path)
    for f in scss_files:
        splitted = f.split(".")
        if len(splitted) == 2:                # then file
            name = splitted[0]
            scss_path = scss + relative_path + '/' + f
            compiled_path = compiled + relative_path + '/' + name + ".css"
            command = "sass " + scss_path + " " + compiled_path
            os.system(command)
        else:                               # then folder
            directory_relative_path = relative_path + "/" + splitted[0]
            full_path = compiled + directory_relative_path
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            compileFolder(directory_relative_path)

compileFolder('')

replace(master_variables_file, new_static, old_static)
