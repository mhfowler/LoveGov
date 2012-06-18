########################################################################################################################
########################################################################################################################
#
#           Form Fields
#
#
########################################################################################################################
########################################################################################################################

# django
from django import forms
from django.forms.extras.widgets import SelectDateWidget

# lovegov
from lovegov.modernpolitics.models import *
from lovegov.modernpolitics.widgets import *

########################################################################################################################
########################################################################################################################

########################################################################################################################
########################################################################################################################
#
# REGISTRATION FORM FIELDS
#
########################################################################################################################
########################################################################################################################

# HTML STYLE VARIABLES
REGISTER_STYLE_CLASS_CHARFIELDS = 'bodyinputboxes'
REGISTER_STYLE_CLASS_SELECT = 'stylebirthday'
# HTML STYLE VARIABLES
LOGIN_STYLE_CLASS_CHARFIELDS = 'logintextfield'

#=======================================================================================================================
# RegisterNameField
#   -
#
#=======================================================================================================================
class RegisterNameField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterNameField, self).__init__(*args, **kwargs)
        self.max_length=100
        self.required=True
        self.widget=forms.TextInput(attrs={'class': REGISTER_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*Your name is required.'}

    #-------------------------------------------------------------------------------------------------------------------
    # Converts input data into a python object: string -> string
    #   @param  value   the string value entered into the field
    #   @return string
    #-------------------------------------------------------------------------------------------------------------------
    def to_python(self,value):
        if not value:
            return []
        return value


#=======================================================================================================================
# RegisterEmailField
#   -
#
#=======================================================================================================================
class RegisterEmailField(forms.EmailField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterEmailField, self).__init__(*args, **kwargs)
        self.max_length=125
        self.required=True
        self.widget=forms.TextInput(attrs={'class': REGISTER_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*Your e-mail is required.'}


#=======================================================================================================================
# RegisterPasswordField
#   -
#
#=======================================================================================================================
class RegisterPasswordField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterPasswordField, self).__init__(*args, **kwargs)
        self.max_length=25
        self.required=True
        self.widget=forms.PasswordInput(attrs={'class': REGISTER_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*You must enter a password.'}

    #-------------------------------------------------------------------------------------------------------------------
    # Validates the date after it has been converted into a python object
    #   @param  value   the python object to be validated
    #   @raise ValidationError
    #-------------------------------------------------------------------------------------------------------------------
    def validate(self, value):
        if not value:
            raise forms.ValidationError(u'Please enter a password')


#=======================================================================================================================
# LoginEmailField
#   -
#
#=======================================================================================================================
class LoginEmailField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(LoginEmailField, self).__init__(*args, **kwargs)
        self.max_length=125
        self.required=True
        self.widget=forms.TextInput(attrs={'class':LOGIN_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*You must enter your e-mail to log in'}


#=======================================================================================================================
# LoginPasswordField
#   -
#
#=======================================================================================================================
class LoginPasswordField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(LoginPasswordField, self).__init__(*args, **kwargs)
        self.max_length=25
        self.required=True
        self.widget=forms.PasswordInput(attrs={'class':LOGIN_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*You must enter your password to log in'}


#=======================================================================================================================
# RegisterBirthField
#   -
#
#=======================================================================================================================
class RegisterBirthField(forms.DateField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterBirthField, self).__init__(*args, **kwargs)
        self.widget=SelectDateWidget(attrs={'class': REGISTER_STYLE_CLASS_SELECT}, years=[y for y in range(1995,1901, -1)])
        self.required=True
        self.error_messages={'required': "*Your birthday is required."}

    #-------------------------------------------------------------------------------------------------------------------
    # Converts input data into a python object: string -> list(string)
    #   @param  value   the string value entered into the field
    #   @return list(string)
    #-------------------------------------------------------------------------------------------------------------------
    def to_python(self, value):
        if not value:
            return []
        return str(value).split('-')

    #-------------------------------------------------------------------------------------------------------------------
    # Validates the date after it has been converted into a python object
    #   @param  value   the python object to be validated
    #   @raise ValidationError
    #-------------------------------------------------------------------------------------------------------------------
    def validate(self, value):
        if not value:
            raise forms.ValidationError(u'Please select your birth year, month, and day')
        dob_year = int(value[0])
        if (dob_year == 0):
            raise forms.ValidationError(u'Please select a birth year')
        dob_month = int(value[1])
        if (dob_month == 0):
            raise forms.ValidationError(u'Please select a birth month')
        dob_day = int(value[2])
        if (dob_day == 0):
            raise forms.ValidationError(u'Please select a birth day')


#=======================================================================================================================
# RegisterSecurityQField
#   -
#
#=======================================================================================================================
class RegisterSecurityQField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterSecurityQField, self).__init__(*args, **kwargs)
        self.max_length=150
        self.required=True
        self.widget=forms.TextInput(attrs={'class': REGISTER_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*You must enter a security question.'}


#=======================================================================================================================
# RegisterSecurityQField
#   -
#
#=======================================================================================================================
class RegisterSecurityAField(forms.CharField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(RegisterSecurityAField, self).__init__(*args, **kwargs)
        self.max_length=50
        self.required=True
        self.widget=forms.PasswordInput(attrs={'class': REGISTER_STYLE_CLASS_CHARFIELDS})
        self.error_messages={'required': '*You must enter a security answer.'}


########################################################################################################################
########################################################################################################################
#
# LOGIN FORM FIELDS
#
########################################################################################################################
########################################################################################################################



########################################################################################################################
########################################################################################################################
#
# COMMENT FORM FIELDS
#
########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# CommentTextField
#   -
#
#=======================================================================================================================
class CommentTextField(forms.Textarea):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(CommentTextField, self).__init__(*args, **kwargs)
        self.required=True
        self.error_messages={'required': '*You must enter your e-mail to log in'}


#=======================================================================================================================
# CommentOnContentField
#   -
#
#=======================================================================================================================
class CommentOnContentField(forms.IntegerField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   - no args
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(CommentOnContentField, self).__init__(*args, **kwargs)
        self.required=True
        self.widget=forms.HiddenInput()


########################################################################################################################
########################################################################################################################
#
# CREATE CONTENT FORM
#
########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# CommentOnContentField
#   -
#
#=======================================================================================================================
class SelectTopicsField(forms.ModelMultipleChoiceField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   @content_type   the type of content
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self,content_type, *args, **kwargs):
        topics = Topic.objects.all()
        super(SelectTopicsField, self).__init__(queryset=topics)
        self.required=True
        self.widget = TopicCheckboxSelectMultiple(content_type=content_type, topic_count=Topic.objects.count())
        self.error_messages={'required': 'You must select a topic.'}

#=======================================================================================================================
# SelectDateTimeField
#   -
#
#=======================================================================================================================
class SelectDateTimeField(forms.DateTimeField):

    #-------------------------------------------------------------------------------------------------------------------
    # Constructor
    #   @content_type   the type of content
    #-------------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        date_formats = ('%m/%d/%y %H:%M am', '%m/%d/%y %H:%M pm')
        super(SelectDateTimeField, self,).__init__(input_formats=date_formats)
        self.required=True
        self.error_messages={'required': '*A date and time is required.'}

    #-------------------------------------------------------------------------------------------------------------------
    # Converts input data into a python object: string -> datetime
    #   @param  value   the string value entered into the field
    #   @return datetime
    #-------------------------------------------------------------------------------------------------------------------
    def to_python(self, value):
        if not value:
            return []
        date = str(value).split('/')
        month = int(date[0])
        day = int(date[1])
        year_time = str(date[2]).split()
        year = int(year_time[0])
        time = str(year_time[1]).split(":")
        hour = int(time[0])
        minute = int(time[1])
        am_pm = year_time[2]
        if am_pm == 'pm':
            hour += 12
        date_object = datetime.datetime(year,month,day,hour,minute)
        return date_object





