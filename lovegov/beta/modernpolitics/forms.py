########################################################################################################################
########################################################################################################################
#
#           Forms
#
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

from lovegov.beta.modernpolitics.forms_fields import *

from django.forms import widgets
from django.contrib import auth
from django import forms
from lovegov.beta.modernpolitics import backend
from django.http import *
from lovegov.beta.modernpolitics.constants import TYPE_DICT
from django.core.files.base import ContentFile
from lovegov.beta.modernpolitics import send_email
from django.forms.widgets import CheckboxInput
import string

logger = logging.getLogger('filelogger')

########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# ValidEmail list
#=======================================================================================================================
class EmailListForm(forms.Form):
    # PRIVATE CLASSES
    class Meta:
        model = EmailList
        fields = ('email')
        # METHODS
    # FIELDS
    email = forms.EmailField()

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        return self.checkEmail()

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if the email entered is a valid Brown e-mail
    #-------------------------------------------------------------------------------------------------------------------
    def checkEmail(self):
        return self.cleaned_data

    def save(self):
        if EmailList.objects.filter(email=self.cleaned_data['email']) is None:
            newEmail = EmailList(email=self.cleaned_data['email'])
            newEmail.save()

#=======================================================================================================================
# Form for create user
#=======================================================================================================================
class CreateUserForm(forms.Form):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=True)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=True)
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=True, initial=constants.DEFAULT_INVITE_SUBJECT)
    message = forms.CharField(widget=forms.Textarea(attrs={'style':'width:225px'}),required=True, initial=constants.DEFAULT_INVITE_MESSAGE)

    def checkUserExists(self):
        return ControllingUser.objects.filter(username=self.cleaned_data['email']).exists()

    def save(self):
        if not ControllingUser.objects.filter(username=self.cleaned_data['email']).exists():
            first_name = self.cleaned_data['firstname']
            name = self.cleaned_data['firstname'] + " " + self.cleaned_data['lastname']
            email = self.cleaned_data['email']
            message = self.cleaned_data['message']
            subject = self.cleaned_data['subject']
            password = backend.generateRandomPassword(8)
            controllingUser = backend.createUser(name, email, password)
            controllingUser.user_profile.basicinfo.invite_message = message
            controllingUser.user_profile.basicinfo.invite_subject = subject
            controllingUser.user_profile.basicinfo.save()
            dict = {'firstname':first_name,'email':email,'password':password,'message':message}
            send_email.sendTemplateEmail(subject,'alphaInvite.html',dict,'team@lovegov.com',email)

#=======================================================================================================================
# Form for search
#=======================================================================================================================
class SearchUserForm(forms.Form):
    firstname = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=False)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=False)

    def searchUserProfiles(self):
        if self.is_valid():
            firstname = self.cleaned_data['firstname']
            lastname = self.cleaned_data['lastname']
            if firstname == "" and lastname != "":
                queryset = UserProfile.objects.filter(last_name=lastname).values('id','first_name','last_name')
            elif firstname != "" and lastname == "":
                queryset = UserProfile.objects.filter(first_name=firstname).values('id','first_name','last_name')
            elif firstname != "" and lastname != "":
                queryset = UserProfile.objects.filter(first_name=firstname,last_name=lastname).values('id','first_name','last_name')
            else:
                queryset = []
            return list(queryset)


#=======================================================================================================================
# Form for register
#=======================================================================================================================
class RegisterForm(forms.Form):
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(required=True)
    passwordregister = forms.CharField(widget=forms.PasswordInput,required=True)
    registercode = forms.CharField(required=False)
    privacy = forms.BooleanField(error_messages={'required': '<<<'})

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(RegisterForm,self).clean()
        email = cleaned_data.get("email")
        email2 = cleaned_data.get("email2")
        register_code = cleaned_data.get("registercode")
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get('lastname')

        if not firstname:
            self._errors["firstname"] = self.error_class([u"Please Enter your First Name."])
        else:
            firstname = firstname.strip()
            if firstname.count(" ") > 1:
                self._errors["firstname"] = self.error_class([u"First Name can only have 1 space"])

        if not lastname:
            self._errors["lastname"] = self.error_class([u"Please Enter your Last Name."])
        else:
            lastname = lastname.strip()
            if lastname.count(" ") > 0:
                self._errors["lastname"] = self.error_class([u"Last Names can't have spaces"])
        msg = ""
        if not (email and email2 and email == email2):
            msg = u"You must enter an email address in both email fields and they must be the same."
        else:
            if not backend.checkUnique(email):
                msg = u"Someone with this e-mail has already registered."
            elif not backend.checkEmail(email) and not backend.checkRegisterCode(register_code):
                msg =u"Our Beta is currently not open to emails with this extension. To register you need to enter a passcode."
                self._errors["registercode"] = self.error_class([u"The register code you entered was not valid."])
        if msg:
            self._errors["email"] = self.error_class([msg])
            self._errors["email2"] = self.error_class([msg])
        return cleaned_data

    def save(self):
        firstname = string.capitalize(self.cleaned_data['firstname'])
        lastname = string.capitalize(self.cleaned_data['lastname'])
        fullname = firstname + " " + lastname
        email = self.cleaned_data['email']
        password = self.cleaned_data['passwordregister']
        user = backend.createUser(fullname,email,password,active=False)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        if 'registerCode' in self.cleaned_data:
            registercode = self.cleaned_data['registercode']
            user_profile = user.user_profile
            user_profile.registration_code = RegisterCode.objects.get(code_text=registercode)
            user_profile.save()
            new_valid_email = ValidEmail(email=email,description="User registered using code: " + registercode)
            new_valid_email.save()
        dict = {'firstname':firstname,'link':user.user_profile.confirmation_link}
        send_email.sendTemplateEmail("LoveGov Confirmation E-Mail","confirmLink.html",dict,"info@lovegov.com",user.username)


#=======================================================================================================================
# Form for logging in.
#=======================================================================================================================
class LoginForm(forms.Form):
    username = LoginEmailField()
    password = LoginPasswordField()

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.has_key("username") and cleaned_data.has_key("password"):
            user = auth.authenticate(username=cleaned_data.get("username"), password=cleaned_data.get("password"))
            if user is None or not user.is_active:
                error_msg = u"That email and password do not match our records. Check for a typo, if not registering is easy too."
                self._errors["username"] = self.error_class([error_msg])
                self._errors["password"] = self.error_class([error_msg])
                del cleaned_data["password"]
        return cleaned_data

#=======================================================================================================================
# Form for changing password.
#=======================================================================================================================
class PasswordForm(forms.Form):
    old = LoginPasswordField()
    new1 = LoginPasswordField()
    new2 = LoginPasswordField()

    def process(self, request):
        if self.is_valid():
            old = self.cleaned_data['old']
            new1 = self.cleaned_data['new1']
            new2 = self.cleaned_data['new2']
            user = request.user
            if user.check_password(old):
                # check if two new passwords are the same
                if new1 == new2:
                    user.set_password(new1)
                    user.save()
                    backend.sendPasswordChangeEmail(user, new1)
                    return True
                else:
                    error_msg = u"The two new passwords you entered were not the same."
                    self._errors["new2"] = self.error_class([error_msg])
                    return False
            else:
                error_msg = u"The old password you entered was not correct. Try again?"
                self._errors["old"] = self.error_class([error_msg])
                return False
        else: return False



#=======================================================================================================================
# Create forms
#=======================================================================================================================
class CreateContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title','topics', 'type')
    def complete(self,request, object=None):
        from lovegov.old.views import getUserProfile, getPrivacy
        if not object:
            object = self.save(commit=False)
        creator = getUserProfile(request)
        privacy = getPrivacy(request)
        object.autoSave(creator=creator, privacy=privacy)
        self.save_m2m()
        object.main_topic = object.getMainTopic()
        object.save()
        return object
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')

class CreatePetitionForm(CreateContentForm):
    class Meta:
        model = Petition
        fields = ('title', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['petition'])

class CreateEventForm(CreateContentForm):
    class Meta:
        model = Event
        fields = ('title', 'full_text', 'datetime_of_event', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['event'])

class CreateNewsForm(CreateContentForm):
    class Meta:
        model = News
        fields = ('title', 'link', 'summary', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['news'])
    def complete(self, request):
        object = self.save(commit=False)
        if 'description' in request.POST:
            object.link_summary = request.POST['description']
        if 'screenshot' in request.POST:
            ref = str(request.POST['screenshot'])
            if ref != 'undefined':
                object.saveScreenShot(ref)
        return super(CreateNewsForm, self).complete(request, object=object)

class CreateMotionForm(CreateContentForm):
    class Meta:
        model = Motion
        fields = ('title', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['motion'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['motion'])

class CreateGroupForm(CreateContentForm):
    class Meta:
        model = Group
        fields = ('title', 'full_text', 'topics', 'group_type', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['group'])




#=======================================================================================================================
# Edit
#=======================================================================================================================
class EditContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title','topics', 'type')
        # METHODS
    def complete(self,request):
        from lovegov.old.views import getPrivacy
        to_return = self.save()
        # save edited relationship
        to_return.saveEdited(privacy=getPrivacy(request))
        return to_return
    action = forms.CharField(widget=forms.HiddenInput(), initial='edit')

class EditPetitionForm(EditContentForm):
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text','topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['petition'])

class EditEventForm(EditContentForm):
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text',  'datetime_of_event', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['event'])

class EditNewsForm(EditContentForm):
    class Meta:
        model = News
        fields = ('title', 'summary', 'link',  'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['news'])

class EditMotionForm(EditContentForm):
    class Meta:
        model = Motion
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['motion'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['motion'])

class EditGroupForm(CreateContentForm):
    class Meta:
        model = Group
        fields = ('title', 'summary', 'group_type', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=constants.TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=constants.TYPE_DICT['group'])




#=======================================================================================================================
# Comment Form
#=======================================================================================================================
class CommentForm(forms.Form):
    # FIELDS
    comment = forms.CharField(max_length=1000)
    c_id = forms.IntegerField()
    # SAVE
    def save(self, creator, privacy):
        data = self.cleaned_data
        comment = Comment(text=data['comment'], on_content_id = data['c_id'])
        comment.autoSave(creator=creator, privacy=privacy)
        return comment



















































#=======================================================================================================================
# Form for registering a new user.
#
#
#=======================================================================================================================
class RegisterForm(forms.Form):
    name = RegisterNameField()
    dob = RegisterBirthField()
    email = RegisterEmailField()
    email2 = RegisterEmailField()
    password = RegisterPasswordField()
    password2 = RegisterPasswordField()
    security_q = RegisterSecurityQField()
    security_a = RegisterSecurityAField()

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        self.checkValidEmail()
        self.checkMatchingFields("email","email2")
        self.checkMatchingFields("password","password2")
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if two fields match in the submitted data and returns appropriate error message.
    #-------------------------------------------------------------------------------------------------------------------
    def checkMatchingFields(self, field1, field2):
        if self.cleaned_data.has_key(field1) and self.cleaned_data.has_key(field2):
            field1_data = self.cleaned_data.get(field1)
            field2_data = self.cleaned_data.get(field2)
            if field1_data != field2_data:
                error_msg = u"Please enter the same " + field1 + u" in both " + field1 + u" fields"
                self._errors[field1] = self.error_class([error_msg])
                self._errors[field2] = self.error_class([error_msg])
                del self.cleaned_data[field1]
                del self.cleaned_data[field2]
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if the email entered is a valid Brown e-mail
    #-------------------------------------------------------------------------------------------------------------------
    def checkValidEmail(self):
        if self.cleaned_data.has_key('email') and self.cleaned_data.has_key('email2'):
            extension = (str(self.cleaned_data['email']).split('@'))[1]
            emailExtension = ValidEmailExtension.objects.filter(extension=extension)
            emailFromList = ValidEmail.objects.filter(email=self.cleaned_data.get('email'))
            if emailExtension.count()==0 and emailFromList.count()==0:
                error_msg = u"Please enter an e-mail flagged for beta testing"
                self._errors['email'] = self.error_class([error_msg])
                self._errors['email2'] = self.error_class([error_msg])
                del self.cleaned_data["email"]
                del self.cleaned_data["email2"]
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # saves a user form form, using default values appropriately.
    # - new_data (form data)
    #-------------------------------------------------------------------------------------------------------------------
    def save(self, new_data):
        # create new UserProfile object with entered email and password
        userProfile = UserProfile.objects.create_user(new_data['email'],'email', new_data['password'])
        # split name into first and last
        names = str.split(new_data['name'])
        userProfile.first_name = names[0]
        if len(names)==2:
            userProfile.last_name = names[1]
        userProfile.is_active = True
        userProfile.save()
        # reference to id of newly created profile
        newid = userProfile.id
        # create user's basic info record
        newBasicInfo = BasicInfo(id=newid)
        birthdate = new_data['dob_year'] + "-" + new_data['dob_month'] + '-' + new_data['dob_day']
        newBasicInfo.dob = birthdate
        newBasicInfo.save()
        #create user's profile page record
        newProfilePage = ProfilePage(person=userProfile)
        newProfilePage.save()
        # create users worldview...
        world_view = WorldView()
        world_view.save()
        userProfile.view_id = world_view.id
        # synchronize id's for all user records
        userProfile.basicinfo_id = newid
        # save random confirmation link (and email to user)
        userProfile.confirmation_link = str(random.randint(1,999999))           # TODO: make cryptographically safe
        userProfile.save()
        return userProfile



########################################################################################################################
########################################################################################################################
#
# Create-Content Forms
#
########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# Content Form
#   - Abstract Form for all Content forms
#
#=======================================================================================================================
class ContentForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')

#=======================================================================================================================
# Petition Form
#
#
#=======================================================================================================================
class PetitionForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        to_return.active = True
        return to_return
    # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['petition'])

#=======================================================================================================================
# Event Form
#
#
#=======================================================================================================================
class EventForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text', 'datetime_of_event', 'topics', 'type')
    # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
    # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['event'])
    datetime_of_event = SelectDateTimeField()

#=======================================================================================================================
# News form.
#
#
#=======================================================================================================================
class NewsForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = News
        fields = ('link', 'title', 'summary', 'topics', 'type')
    # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
    # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['news'])

#=======================================================================================================================
# Group form.
#
#
#=======================================================================================================================
class GroupForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Group
        fields = ('title', 'group_type', 'summary','full_text', 'topics','type')
    # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        to_return.save()
        creator = UserProfile.objects.get(id=request.user.id)
        to_return.admins.add(creator)
        to_return.members.add(creator)
        return to_return
    # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['group'])

#=======================================================================================================================
# Debate form.
#
#
#=======================================================================================================================
class DebateForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Debate
        fields = ('title', 'summary','debate_when')
    # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
    # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['debate'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['debate'])

#=======================================================================================================================
# Album form.
#
#
#=======================================================================================================================
class UserImageForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = UserImage
        fields = ('title', 'summary','topics')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        file_content = ContentFile(request.FILES['image'].read())
        to_return.createImage(file_content)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['image'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['image'])
    image = forms.FileField()


#=======================================================================================================================
# Upload Forms
#
#
#=======================================================================================================================
class UploadFileForm(forms.Form):
    image = forms.FileField()
class UploadImageForm(forms.Form):
    image = forms.ImageField()


########################################################################################################################
# Create-Content-Simple Forms
#
#
########################################################################################################################

class PetitionForm_simple(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='P')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

class EventForm_simple(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    date_of_event = forms.DateTimeField()
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='E')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

class NewsForm_simple(forms.ModelForm):
    class Meta:
        model = News
        fields = ('title', 'summary', 'link', 'topics', 'type')
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='N')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

#=======================================================================================================================
# BasicInfo form
#
#
#=======================================================================================================================
class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
    dob = forms.DateField(required=False,initial=datetime.datetime.now().date())



