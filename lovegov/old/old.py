
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
