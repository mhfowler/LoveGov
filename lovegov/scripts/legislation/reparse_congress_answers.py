#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.scripts.alpha import scriptReparseCongressAnswers
    from lovegov.scripts.alpha import scriptCreateCongressAnswers
    from pprint import pprint

    metrics = scriptReparseCongressAnswers()
