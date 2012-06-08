class SimpleRouter(object):

    def db_for_read(self, model, **hints):
        if model.__name__ == 'EmailList':
            return 'mailinglist'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ == 'EmailList':
            return 'mailinglist'
        return None

    def allow_syncdb(self, db, model):
        if db == 'mailinglist':
            return model.__name__=='EmailList'
        elif model.__name__ == 'EmailList':
            return False
        return None