from lovegov.modernpolitics.backend import *
import cProfile
import pstats

def testComparisonPrep():
    q = Question.objects.all()
    print ("questions: " + str(q.count()))
    randy = getUser("Randy Johnson")
    katy = getUser("Katy Perry")
    #randomAnswers(randy)
    #randomAnswers(katy)
    randy.last_answered = datetime.datetime.now()
    randy.save()

def testComparison():
    randy = getUser("Randy Johnson")
    katy = getUser("Katy Perry")
    return randy.getComparisonJSON(katy)

#testComparisonPrep()
cProfile.run('testComparison()', 'comparison_profile')
p = pstats.Stats('comparison_profile')
p.sort_stats('cumulative').print_stats(20)
print "~~~~~~~~~~~"
p.sort_stats('time').print_stats(20)
print "~~~~~~~~~~~"
p.print_callers(.5, 'init')





