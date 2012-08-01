from lovegov.settings import PROJECT_PATH
from django.conf import settings
import os
import re

css = PROJECT_PATH + '/frontend/static/css'
compiled = css + '/compiled'
scss = css + '/scss'

# modify static_url in master-variables
master_variables_file = scss + '/master-variables.scss'
old_static = re.escape("$STATIC_URL: '/static';")
new_static = re.escape("$STATIC_URL: '" + settings.STATIC_URL + "';")

sed_replace = "'s/" + old_static + "/" + new_static + "/g'"
sed_pre = "sed -i " + sed_replace + " " + master_variables_file
os.system(sed_pre)

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

sed_replace = "'s/" + new_static + "/" + old_static + "/g'"
sed_post = "sed -i " + sed_replace + " " + master_variables_file
os.system(sed_post)