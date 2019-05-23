import zipfile

viya_version = '3.3'
with zipfile.ZipFile('/tmp/license.zip', 'r') as zip_file:
    for file in zip_file.infolist():
        if file.filename.endswith('jwt'):
            viya_version = '3.4'

print viya_version
