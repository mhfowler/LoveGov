import s3_configuration
AWS_ACCESS_KEY_ID = s3_configuration.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = s3_configuration.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = s3_configuration.AWS_STORAGE_BUCKET_NAME

STATICFILES_STORAGE = 'storage.CachedS3BotoStorage'

DEFAULT_S3_PATH = "media"
STATIC_S3_PATH = "static"

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 
                        'compressor.filters.cssmin.CSSMinFilter',
                        'compressor.filters.template.TemplateFilter']

COMPRESS_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
COMPRESS_OUTPUT_DIR = 'CACHE' # default, included for simplicity
COMPRESS_STORAGE = STATICFILES_STORAGE

COMPRESS_ROOT = "LoveGov/frontend/"