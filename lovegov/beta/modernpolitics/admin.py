
### INTERNAL ###
from lovegov.beta.modernpolitics.models import Question, Answer, Topic, NextQuestion

### DJANGO ###
from django.contrib import admin

# makes admin site use qaweb db... inherit from this
class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'default'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(MultiDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)

# Specialize the multi-db admin objects for use with specific models.
class QuestionAdmin(MultiDBModelAdmin):
    model = Question

class AnswerAdmin(MultiDBModelAdmin):
    model = Answer

class TopicAdmin(MultiDBModelAdmin):
    model = Topic

class NextQuestionAdmin(MultiDBModelAdmin):
    model = NextQuestion

# admin editable
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(NextQuestion, NextQuestionAdmin)