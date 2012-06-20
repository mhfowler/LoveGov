from lovegov.settings import PROJECT_PATH
import os

css = PROJECT_PATH + '/frontend/static/css'
compiled = css + '/compiled'
scss = css + '/scss'
scss_files = os.listdir(scss)

for f in scss_files:
    splitted = f.split(".")
    name = splitted[0]
    scss_path = scss + '/' + f
    compiled_path = compiled + '/' + name + ".css"
    command = "sass " + scss_path + " " + compiled_path
    os.system(command)
