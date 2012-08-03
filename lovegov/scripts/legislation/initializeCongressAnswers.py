


if __name__ == "__main__":
    from lovegov.modernpolitics.scripts.alpha import scriptCreateCongressAnswers
    from pprint import pprint

    print "================= scriptCreateCongressAnswers() ======================="
    print '======================================================================='
    metrics = scriptCreateCongressAnswers()
    print "======================= Metrics ========================"
    print '========================================================'
    pprint(metrics)