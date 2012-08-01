from lovegov.bash import s3upload

test_folder = '/Users/maxfowler/Desktop/cs/s3test'
args = ['test', test_folder]
s3upload.run(args=args)