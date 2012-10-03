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

class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/news.txt')

    def get_model(self):
        return News

    def index_queryset(self):
        return self.get_model().objects.all()

class GroupIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/indexes/group.txt')
    hidden = indexes.CharField(model_attr='hidden')
    group_type = indexes.CharField(model_attr='group_type')

    def get_model(self):
        return Group

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare_hidden(self, obj):
        # For some reason, this is necessary
        if obj.hidden:
            return 'True'
        else:
            return 'False'

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

