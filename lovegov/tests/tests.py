from lovegov.modernpolitics.backend import *
from django.core.management import call_command

import unittest


def testAnswer(user1, user2, question, same=True, weight1=5, weight2=5):
    answers = question.answers.all()
    if same:
        a1 = answers[0]
        a2 = answers[0]
    else:
        a1 = answers[0]
        a2 = answers[1]
    answerAction(user=user1, question=question, my_response=None,
        privacy='PUB', answer_id=a1.id, weight=weight1, explanation="")
    answerAction(user=user2, question=question, my_response=None,
        privacy='PUB', answer_id=a2.id, weight=weight2, explanation="")


class ComparisonTestCase(unittest.TestCase):

    fixtures = ['test_fixture.json']

    def setUp(self):
        print "load fixture!"
        call_command("loaddata", "test_fixture.json", verbosity=0)

    def testIdentity(self):
        q = Question.objects.all()
        print ("# of questions: " + str(q.count()))
        katy = getUser("Katy Perry")
        randomAnswers(katy)
        comparison = katy.getComparison(katy)
        self.assertEqual(comparison.result, 100)

    def testIdenticalComparison(self):
        katy = getUser("Katy Perry")
        randy = getUser("Randy Johnson")
        katy.clearResponses()
        randy.clearResponses()
        q = Question.objects.all()
        testAnswer(randy, katy, q[0])
        testAnswer(randy, katy, q[1])
        testAnswer(randy, katy, q[2])
        testAnswer(randy, katy, q[3])
        comparison = randy.getComparison(katy)
        self.assertEqual(comparison.result, 100)
        comparison = katy.getComparison(randy)
        self.assertEqual(comparison.result, 100)

    def testFiftyPercentComparison(self):
        katy = getUser("Katy Perry")
        randy = getUser("Randy Johnson")
        katy.clearResponses()
        randy.clearResponses()
        q = Question.objects.all()
        testAnswer(randy, katy, q[0])
        testAnswer(randy, katy, q[1])
        testAnswer(randy, katy, q[2], same=False)
        testAnswer(randy, katy, q[3], same=False)
        comparison = randy.getComparison(katy)
        self.assertEqual(comparison.result, 50)
        comparison = katy.getComparison(randy)
        self.assertEqual(comparison.result, 50)

