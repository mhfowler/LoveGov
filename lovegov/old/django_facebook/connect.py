import logging
from random import randint
import sys

from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import simplejson as json

from lovegov.old.django_facebook.api import get_facebook_graph, FacebookUserConverter
from lovegov.old.django_facebook.utils import ( get_profile_class)

# internal
from modernpolitics.backend import createUser
from modernpolitics.backend import checkEmail, checkUnique
from lovegov.old.django_facebook import signals

logger = logging.getLogger(__name__)
mylogger = logging.getLogger('filelogger')

class CONNECT_ACTIONS:
    class LOGIN:
        pass

    class CONNECT(LOGIN):
        pass

    class REGISTER:
        pass

    class DENIED:
        pass

def connect_user(request, access_token=None, facebook_graph=None):
    '''
    Given a request either

    - (if authenticated) connect the user
    - login
    - register
    '''
    user = None
    graph = facebook_graph or get_facebook_graph(request, access_token)
    facebook = FacebookUserConverter(graph)

    assert facebook.is_authenticated()
    facebook_data = facebook.facebook_profile_data()
    force_registration = request.REQUEST.get('force_registration') or\
        request.REQUEST.get('force_registration_hard')

    logger.debug('force registration is set to %s', force_registration)
    mylogger.error("the test!!")
    if request.user.is_authenticated() and not force_registration:
        action = CONNECT_ACTIONS.CONNECT
        user = _connect_user(request, facebook)
    else:
        email = facebook_data.get('email', False)
        mylogger.error("email: " + email)
        email_verified = facebook_data.get('verified', False)
        kwargs = {}
        if email and email_verified:
            kwargs = {'facebook_email': email}
        auth_user = authenticate(facebook_id=facebook_data['id'], **kwargs)
        if auth_user and not force_registration:
            action = CONNECT_ACTIONS.LOGIN

            # Has the user registered without Facebook, using the verified FB
            # email address?
            # It is after all quite common to use email addresses for usernames
            if not auth_user.get_profile().facebook_id:
                update = True
            else:
                update = getattr(auth_user, 'fb_update_required', False)
            user = _login_user(request, facebook, auth_user, update=update)
        else:           # email check
############################# ############################# ############################# #############################
            if checkEmail(email):
                if checkUnique(email):
                    print("register")
                    mylogger.error("register!")
                    action = CONNECT_ACTIONS.REGISTER
                    # when force registration is active we should clearout
                    # the old profile
                    user = _register_user(request, facebook,
                        remove_old_connections=force_registration)
                else:
                    action = CONNECT_ACTIONS.DENIED
                    user = "Your facebook account is registered with the email " + email + ". There is already a registered\
                    lovegov user with that email. If you are that user and would like to associate your facebook with that\
                    account please login as that user and then click to sign in through facebook again."
            else:
                print("denied")
                action = CONNECT_ACTIONS.DENIED
                user = "Your facebook account is registered with the email " + email + ". This email is not in one\
                    of our accepted networks yet. If you have the passcode, you can still register without facebook below."
                return action, user
############################# ############################# ############################# #############################

    #store likes and friends if configured
    sid = transaction.savepoint()
    try:
        if facebook_settings.FACEBOOK_STORE_LIKES:
            facebook.get_and_store_likes(user)
        if facebook_settings.FACEBOOK_STORE_FRIENDS:
            facebook.get_and_store_friends(user)
        transaction.savepoint_commit(sid)
    except IntegrityError, e:
        logger.warn(u'Integrity error encountered during registration, '
                'probably a double submission %s' % e,
            exc_info=sys.exc_info(), extra={
            'request': request,
            'data': {
                 'body': unicode(e),
             }
        })
        transaction.savepoint_rollback(sid)

    profile = user.get_profile()
    #store the access token for later usage if the profile model supports it
    if hasattr(profile, 'access_token'):
        # only update the access token if it is long lived or we are set to store all
        if not graph.expires or facebook_settings.FACEBOOK_STORE_ALL_ACCESS_TOKENS:
            # and not equal to the current token
            if graph.access_token != profile.access_token:
                profile.access_token = graph.access_token
                profile.save()
        
        #warn if we didn't get offline access
        if graph.expires:
            logger.warn('we shouldnt be finding a graph expiration, its set to %s', graph.expires)

    return action, user


def _login_user(request, facebook, authenticated_user, update=False):
    login(request, authenticated_user)

    if update:
        _connect_user(request, facebook)

    return authenticated_user


def _connect_user(request, facebook):
    '''
    Update the fields on the user model and connects it to the facebook account

    '''
    if not request.user.is_authenticated():
        raise ValueError(
            'Connect user can only be used on authenticated users')
    if not facebook.is_authenticated():
        raise ValueError(
            'Facebook needs to be authenticated for connect flows')

    user = _update_user(request.user, facebook)

    return user


def _register_user(request, facebook, profile_callback=None,
                   remove_old_connections=False):
    '''
    Creates a new user and authenticates
    The registration form handles the registration and validation
    Other data on the user profile is updates afterwards

    if remove_old_connections = True we will disconnect old
    profiles from their facebook flow
    '''


    if not facebook.is_authenticated():
        raise ValueError(
            'Facebook needs to be authenticated for connect flows')

    # get the backend on new registration systems, or none
    # if we are on an older version
    """ django-registration
    backend = get_registration_backend()

    # gets the form class specified in FACEBOOK_REGISTRATION_FORM
    form_class = get_form_class(backend, request)
    """
    facebook_data = facebook.facebook_registration_data()

    data = request.POST.copy()
    for k, v in facebook_data.items():
        if not data.get(k):
            data[k] = v
        # for testing
        print "data[" + str(k) +"]: " + str(data[k])
    if remove_old_connections:
        _remove_old_connections(facebook_data['facebook_id'])

    if request.REQUEST.get('force_registration_hard'):
        data['email'] = data['email'].replace(
            '@', '+test%s@' % randint(0, 1000000000))

        """ register with form
    form = form_class(data=data, files=request.FILES,
        initial={'ip': request.META['REMOTE_ADDR']})

    if not form.is_valid():
        error = facebook_exceptions.IncompleteProfileError('Facebook data %s '
            'gave error %s' % (facebook_data, form.errors))
        error.form = form
        raise error
        """

    #for new registration systems use the backends methods of saving
    """
    if backend:
        new_user = backend.register(request, **form.cleaned_data)
    else:
        # For backward compatibility, if django-registration form is used
        try:
            new_user = form.save(profile_callback=profile_callback)
        except TypeError:
            new_user = form.save()
    """

    # createuser TODO: figure out how and where to set actual password.
    new_user = createUser(name=data['name'], email=data['email'], password='password')
    new_user.user_profile.confirmed = True   # we assume facebook email is confirmed
    new_user.user_profile.save()

    signals.facebook_user_registered.send(sender=auth.models.User,
        user=new_user, facebook_data=facebook_data)

    #update some extra data not yet done by the form
    new_user = _update_user(new_user, facebook)

    # IS this the correct way for django 1.3? seems to require the backend
    # attribute for some reason
    new_user.backend = 'lovegov.beta.django_facebook.auth_backends.FacebookBackend'
    auth.login(request, new_user)

    return new_user


def _remove_old_connections(facebook_id, current_user_id=None):
    '''
    Removes the facebook id for profiles with the specified facebook id
    which arent the current user id
    '''
    profile_class = get_profile_class()
    other_facebook_accounts = profile_class.objects.filter(
        facebook_id=facebook_id)
    if current_user_id:
        other_facebook_accounts = other_facebook_accounts.exclude(
            user__id=current_user_id)
    other_facebook_accounts.update(facebook_id=None)


def _update_user(user, facebook):
    '''
    Updates the user and his/her profile with the data from facebook
    '''
    # if you want to add fields to ur user model instead of the
    # profile thats fine
    # partial support (everything except raw_data and facebook_id is included)
    facebook_data = facebook.facebook_registration_data(username=False)
    facebook_fields = ['facebook_name', 'facebook_profile_url', 'gender',
        'date_of_birth', 'about_me', 'website_url', 'first_name', 'last_name']
    user_dirty = profile_dirty = False
    profile = user.get_profile()

    signals.facebook_pre_update.send(sender=get_profile_class(),
        profile=profile, facebook_data=facebook_data)

    profile_field_names = [f.name for f in profile._meta.fields]
    user_field_names = [f.name for f in user._meta.fields]

    #set the facebook id and make sure we are the only user with this id
    if facebook_data['facebook_id'] != profile.facebook_id:
        logger.info('profile facebook id changed from %s to %s',
                    repr(facebook_data['facebook_id']),
                    repr(profile.facebook_id))
        profile.facebook_id = facebook_data['facebook_id']
        profile_dirty = True
        _remove_old_connections(profile.facebook_id, user.id)

    #update all fields on both user and profile
    for f in facebook_fields:
        facebook_value = facebook_data.get(f, False)
        print("f[" + str(f) + "]: " + str(facebook_value))
        if facebook_value:
            if (f in profile_field_names and hasattr(profile, f) and
                not getattr(profile, f, False)):
                logger.debug('profile field %s changed from %s to %s', f,
                             getattr(profile, f), facebook_value)
                setattr(profile, f, facebook_value)
                profile_dirty = True
            elif (f in user_field_names and hasattr(user, f) and
                  not getattr(user, f, False)):
                logger.debug('user field %s changed from %s to %s', f,
                             getattr(user, f), facebook_value)
                setattr(user, f, facebook_value)
                user_dirty = True

    #write the raw data in case we missed something
    if hasattr(profile, 'raw_data'):
        serialized_fb_data = json.dumps(facebook.facebook_profile_data())
        if profile.raw_data != serialized_fb_data:
            logger.debug('profile raw data changed from %s to %s',
                         profile.raw_data, serialized_fb_data)
            profile.raw_data = serialized_fb_data
            profile_dirty = True

    #save both models if they changed
    if user_dirty:
        user.save()
    if profile_dirty:
        profile.save()

    signals.facebook_post_update.send(sender=get_profile_class(),
        profile=profile, facebook_data=facebook_data)

    return user
