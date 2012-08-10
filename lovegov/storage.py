from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage
from s3_folder_storage.s3 import StaticStorage
import local_settings

class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
    	kwargs['location'] = local_settings.STATIC_S3_PATH
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name