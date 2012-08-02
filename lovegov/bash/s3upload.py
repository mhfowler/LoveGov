import sys
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from lovegov import s3_configuration
from django.conf import settings

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def uploadFile(path, rel_path, bucket):
    print 'Uploading %s' % path
    already = bucket.get_key(rel_path)
    if already:
        print "replacing."
    k = Key(bucket)
    k.key = rel_path
    k.set_contents_from_filename(path,cb=percent_cb, num_cb=10)

def run(args):
    origin_folder = args[1]
    if len(args) > 2:
        destination_folder = args[2]
    else:
        destination_folder = 'media/'
    conn = S3Connection(s3_configuration.AWS_ACCESS_KEY_ID, s3_configuration.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_configuration.AWS_STORAGE_BUCKET_NAME)
    for dirpath, dirnames, filenames in os.walk(origin_folder):
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel_path = path.replace(origin_folder, destination_folder, 1)
            uploadFile(path, rel_path, bucket)

if len(sys.argv) < 2:
    run(sys.argv)
else:
    print "not enough arguments."

