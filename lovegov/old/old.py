
#=======================================================================================================================
# Form for registering.
#=======================================================================================================================
class SimpleRegisterForm(forms.Form):
    name = RegisterNameField()
    email = RegisterEmailField()
    password = RegisterPasswordField()
    #-------------------------------------------------------------------------------------------------------------------
    # Checks valid email, and adds errors if necessary and sends us request email.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        # custom clean
        if self.cleaned_data.has_key('email'):
            emailList = ValidEmail.objects.filter(email=self.cleaned_data['email'])
            extension = (str(self.cleaned_data['email']).split('@'))[1]
            emailExtension = ValidEmailExtension.objects.filter(extension=extension)
            # if not valid extension or on list give error message and send request to join email
            if not (emailList or emailExtension):
                error_msg = u"This email isn't in our Beta records. We are currently testing the site with a limited number of users. We will let you know when you can join!"
                self._errors['email'] = self.error_class([error_msg])
                # save email
                save_email = EmailList(email=self.cleaned_data['email'])
                save_email.save()
            else:
                if emailList:
                    self.confirmedEmail = True  # THIS IS BAD ASSUMPTION will change
                if emailExtension:
                    self.confirmedEmail = False
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Saves new user and emails confirmation link appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def save(self):
        data = self.cleaned_data    # for ease of reference
        control = backend.createUserHelper(name=data['name'], email=data['email'], password=data['password'])
        # set authentication backend (not facebook)
        control.backend = 'django.contrib.auth.backends.ModelBackend'
        control.save()
        userProfile = control.user_profile
        if self.confirmedEmail:
            userProfile.confirmed = True
            userProfile.save()
            return control
        else:
            userProfile.confirmed = False
            userProfile.save()
            backend.sendConfirmationEmail(userProfile=userProfile)
            return None











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



