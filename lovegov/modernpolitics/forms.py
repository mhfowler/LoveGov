########################################################################################################################
########################################################################################################################
#
#           Forms
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.forms_fields import *
from lovegov.modernpolitics.defaults import *

# django
from django.contrib import auth
from django.core.files.base import ContentFile

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
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:225px'}),required=True, initial=DEFAULT_INVITE_SUBJECT)
    message = forms.CharField(widget=forms.Textarea(attrs={'style':'width:225px'}),required=True, initial=DEFAULT_INVITE_MESSAGE)

    def checkUserExists(self):
        return ControllingUser.objects.filter(username=self.cleaned_data['email']).exists()

    def save(self):
        from lovegov.modernpolitics.register import createUser
        if not ControllingUser.objects.filter(username=self.cleaned_data['email']).exists():
            first_name = self.cleaned_data['firstname']
            name = self.cleaned_data['firstname'] + " " + self.cleaned_data['lastname']
            email = self.cleaned_data['email']
            message = self.cleaned_data['message']
            subject = self.cleaned_data['subject']
            password = generateRandomPassword(8)
            controllingUser = createUser(name, email, password)
            controllingUser.user_profile.invite_message = message
            controllingUser.user_profile.invite_subject = subject
            controllingUser.user_profile.save()
            vals = {'firstname':first_name,'email':email,'password':password,'message':message}
            sendTemplateEmail(subject,'alphaInvite.html',vals,'team@lovegov.com',email)

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
    fullname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(required=True)
    passwordregister = forms.CharField(widget=forms.PasswordInput,required=True)
    privacy = forms.BooleanField(error_messages={'required': '< click'})

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        email = cleaned_data.get("email")
        email2 = cleaned_data.get("email2")
        fullname = cleaned_data.get('fullname')

        # Handle fullname error checking
        if not fullname:
            self._errors["fullname"] = self.error_class([u"input your full name."])
        else:
            spaces = fullname.count(" ")
            if spaces > 2: self._errors["fullname"] = self.error_class([u"too many spaces in name."])
            elif spaces < 1: self._errors['fullname'] = self.error_class([u"input a first & last name."])
        # Handle email error checking
        if not email:
            self._errors["email"] = self.error_class([u"input your email"])
        if not email2:
            self._errors["email2"] = self.error_class([u"input your email again"])
        if email and email2 and email != email2:
            self._errors["email2"] = self.error_class([u"input same email as inputted above"])
        if not checkUnique(email):
            msg = u"this e-mail is already registered."
            self._errors["email"] = self.error_class([msg])
            self._errors["email2"] = self.error_class([msg])
        return cleaned_data

    def save(self):
        from lovegov.modernpolitics.register import createUser
        fullname = self.cleaned_data['fullname'].split(" ")
        if len(fullname) == 3:
            firstname = string.capitalize(fullname[0]) + " " + string.capitalize(fullname[1])
            lastname = string.capitalize(fullname[2])
            fullname = firstname + " " + lastname
        else:
            firstname = string.capitalize(fullname[0])
            lastname = string.capitalize(fullname[1])
            fullname = firstname + " " + lastname
        email = self.cleaned_data['email']
        password = self.cleaned_data['passwordregister']
        user = createUser(fullname,email,password,active=False)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        vals = {'firstname':firstname,'link':user.user_profile.confirmation_link}
        sendTemplateEmail("LoveGov Confirmation E-Mail","confirmLink.html",vals,"info@lovegov.com",user.username)

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
# Form for reseting your password
#=======================================================================================================================
class RecoveryPassword(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput,required=True)
    password2 = forms.CharField(widget=forms.PasswordInput,required=True)

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        cleaned_data = super(RecoveryPassword, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        none_error = u"Please enter your desired password."
        if not password1: self._errors["password1"] = self.error_class([none_error])
        if not password2: self._errors["password2"] = self.error_class([none_error])
        if password1 and password2 and password1 != password2:
            match_error = u"Passwords don't match"
            self._errors["password1"] = self.error_class([match_error])
            self._errors["password2"] = self.error_class([match_error])

        return cleaned_data

    def save(self,confirm_link):
        from modernpolitics.models import ResetPassword
        resetPassword = ResetPassword.lg.get_or_none(email_code=confirm_link)
        if resetPassword:
            user= resetPassword.userProfile.user
            user.set_password(self.cleaned_data['password1'])
            user.save()
            resetPassword.delete()
            return user.username

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
                    sendPasswordChangeEmail(user, new1)
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
        fields = ('title', 'full_text', 'topics', 'type','scale')
    topics = SelectTopicsField(content_type=TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['petition'])

class CreateEventForm(CreateContentForm):
    class Meta:
        model = Event
        fields = ('title', 'full_text', 'datetime_of_event', 'topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['event'])

class CreateNewsForm(CreateContentForm):
    class Meta:
        model = News
        fields = ('title', 'link', 'summary', 'topics', 'type','scale')
    topics = SelectTopicsField(content_type=TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['news'])
    def complete(self, request):
        object = self.save(commit=False)
        if 'description' in request.POST:
            object.link_summary = request.POST['description']
        if 'screenshot' in request.POST:
            ref = str(request.POST['screenshot'])
            if ref != 'undefined':
                object.saveScreenShot(ref)
        return super(CreateNewsForm, self).complete(request, object=object)

class CreateUserGroupForm(CreateContentForm):
    class Meta:
        model = UserGroup
        fields = ('title', 'full_text', 'topics', 'group_type', 'type', 'group_privacy','scale')
    topics = SelectTopicsField(content_type=TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['group'])
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')
    group_type = forms.CharField(widget=forms.HiddenInput(), initial='U')


class CreateMotionForm(CreateContentForm):
    class Meta:
        model = Motion
        fields = ('title', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['motion'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['motion'])

#=======================================================================================================================
# Comment Form
#=======================================================================================================================
class CommentForm(forms.Form):
    # FIELDS
    comment = forms.CharField(max_length=10000)
    c_id = forms.IntegerField()
    # SAVE
    def save(self, creator, privacy):
        data = self.cleaned_data
        comment = Comment(text=data['comment'], on_content_id = data['c_id'])
        comment.autoSave(creator=creator, privacy=privacy)
        return comment













#=======================================================================================================================
# Edit
#=======================================================================================================================
class EditContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title','topics', 'type')
        # METHODS
    def complete(self,request):
        to_return = self.save()
        # save edited relationship
        to_return.saveEdited(privacy=getPrivacy(request))
        return to_return
    action = forms.CharField(widget=forms.HiddenInput(), initial='edit')

class EditPetitionForm(EditContentForm):
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text','topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['petition'])

class EditEventForm(EditContentForm):
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text',  'datetime_of_event', 'topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['event'])

class EditNewsForm(EditContentForm):
    class Meta:
        model = News
        fields = ('title', 'summary', 'link',  'topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['news'])

class EditMotionForm(EditContentForm):
    class Meta:
        model = Motion
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    topics = SelectTopicsField(content_type=TYPE_DICT['motion'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['motion'])

class EditUserGroupForm(CreateContentForm):
    class Meta:
        model = UserGroup
        fields = ('title', 'summary', 'group_type', 'full_text', 'topics', 'type', 'group_privacy')
    topics = SelectTopicsField(content_type=TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['group'])


#=======================================================================================================================
# Other forms
#=======================================================================================================================
class UploadFileForm(forms.Form):
    image = forms.FileField()
class UploadImageForm(forms.Form):
    image = forms.ImageField()


class UserImageForm(forms.Form):
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
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')
    topics = SelectTopicsField(content_type=TYPE_DICT['image'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['image'])
    image = forms.FileField()






class EditProfileForm(forms.Form):
    bio = forms.CharField(required=False)
    avatar =  forms.FileField(required=False)



    fullname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(required=True)
    passwordregister = forms.CharField(widget=forms.PasswordInput,required=True)
    privacy = forms.BooleanField(error_messages={'required': '< click'})
    bio = LoginEmailField()
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



































