from open_facebook.api import OpenFacebook
from lovegov.old.django_facebook.tests_utils.sample_data import user_data


class MockFacebookAPI(OpenFacebook):
    mock = True

    def me(self):
        data = user_data[self.access_token]
        return data

    def is_authenticated(self, *args, **kwargs):
        from django_facebook.tests_utils.sample_data.user_data import user_data
        return self.access_token in user_data
