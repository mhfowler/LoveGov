########################################################################################################################
########################################################################################################################
#
#           Search Indexes
#               http://docs.haystacksearch.org/dev/tutorial.html
#
#
########################################################################################################################
########################################################################################################################

# python
from haystack import indexes

# lovegov
from lovegov.modernpolitics.models import *

#=======================================================================================================================
# For searching.
#
#=======================================================================================================================
class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/user.txt')
    content_auto = indexes.EdgeNgramField(model_attr='get_name')

    def get_model(self):
        return UserProfile

    def index_queryset(self):
        return self.get_model().objects.all()

class PetitionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/petition.txt')

    def get_model(self):
        return Petition

    def index_queryset(self):
        return self.get_model().objects.all()

class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/event.txt')

    def get_model(self):
        return Event

    def index_queryset(self):
        return self.get_model().objects.all()

class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/news.txt')

    def get_model(self):
        return News

    def index_queryset(self):
        return self.get_model().objects.all()

class GroupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/group.txt')

    def get_model(self):
        return Group

    def index_queryset(self):
        return self.get_model().objects.all()

class MotionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/motion.txt')

    def get_model(self):
        return Motion

    def index_queryset(self):
        return self.get_model().objects.all()


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/comment.txt')

    def get_model(self):
        return Comment

    def index_queryset(self):
        return self.get_model().objects.all()

class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/question.txt')

    def get_model(self):
        return Question

    def index_queryset(self):
        return self.get_model().objects.all()

