from lovegov.settings import PROJECT_PATH
import os

css = PROJECT_PATH + '/frontend/static/css'
compiled = css + '/compiled'
scss = css + '/scss'

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
