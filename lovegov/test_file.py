""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.views import *
from lovegov.scripts.alpha import scriptCreateCongressAnswers

metrics = scriptCreateCongressAnswers()

