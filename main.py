# /home/photo/hhg/.venv/bin/python3 /home/photo/hhg/main.py /home/photo/inbox /home/photo/media >> /home/photo/log
import os
import time
import exiftool
import datetime
import shutil
import re
import sys
# from imgcat import imgcat
from datetime import datetime

def getfilelist(loc):
    for root, dirs, files in os.walk(loc, topdown=False, followlinks=True):
       for name in files:
          resource = os.path.join(root, name)
          # print(resource)
          yield(resource)
       # for name in dirs:
       #    print(os.path.join(root, name))

def removeempty(loc):
    for root, dirs, files in os.walk(loc, topdown=False, followlinks=True):
        for name in dirs:
            try:
                myfile = os.path.join(root, name)
                if myfile == loc:
                    continue
                if os.path.islink(myfile):
                    os.unlink(myfile)
                elif os.path.isfile(myfile):
                    os.remove(myfile)
                elif os.path.isdir(myfile):
                    os.rmdir(myfile)
            except Exception as exc:
               print('echo ', str(datetime.now()), exc)

def mindate(d1, d2):
    # print('\n\n\n', d1, d2, '\n\n\n')
    if d1.timestamp() > d2.timestamp():
        return d2
    else:
        return d1

def run(src, dst):

    while True:
        time.sleep(5)
        ingest(src, dst)

        # time.sleep(5)
      
def ingest(src, dst):
    os.makedirs(os.path.dirname(src), exist_ok=True)
    if not len(os.listdir(src)):
        print('echo ', str(datetime.now()), "Running ingestion on no files")
        return

    # files = os.listdir(src)

    files = getfilelist(src)
    # print(str(datetime.now()), "Running ingestion on some files")

    with exiftool.ExifTool() as et:
        for file in files:
            source = file
            relative = file.replace(src, '')
            fileonly =  file.rsplit('/', 1)[1]
            try:
                metadata = et.get_metadata(source)
            except Exception as e:
                print('echo ', str(datetime.now()), source)
                print('echo ', str(datetime.now()), e)
                continue
            try:
                # print(str(metadata.keys()))
                datefields = [
                    'EXIF:DateTimeOriginal',
                    'EXIF:CreateDate',
                    'Quicktime:CreateDate',
                    'Quicktime:CreationDate'
                ]
                timestamp = datetime.now()
                x = timestamp
                for datefield in datefields:
                    timestamp_str = metadata.get(datefield)
                    if not timestamp_str:
                        continue
                    timestamp = mindate(timestamp, datetime.strptime(timestamp_str,"%Y:%m:%d %H:%M:%S"))
                if timestamp == x:
                    raise Exception
                serial = metadata.get('EXIF:SerialNumber') #metadata.get('EXIF:')
                model = metadata.get('EXIF:Model')
                device = '(model)'
                if model and serial:
                    device = '%s:%s' % (model, serial)
                elif model:
                    device = model
                elif serial:
                    device = serial
                target = "%s/%s/%04d/%02d/%02d/%s" % (dst, device, timestamp.year, timestamp.month, timestamp.day, fileonly)

                try:
                    # print('echo "%s: %s >> %s"\n' % (str(datetime.now()), source, target))
                    print('%s' % ('imgcat --height 5 "%s"' % target))
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.move(source, target)
                    # imgcat(open(target), height=2)
                    # os.remove(source)
                except Exception as e:
                    print('echo Failed to move %s' % source, str(datetime.now()), e, source, target)

            except Exception as e:
                print('echo Failed to assess EXIF %s' % source, str(datetime.now()), e)
                # print(metadata.keys())
                # raise(e)
                target = '%s/error/%s' % (dst, relative)
                # print(target)
                target = re.sub(r'/error/.*/?error/', '/error/', target)
                # print('>>', target)
                try:
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.move(source, target)
                    print('echo ', str(datetime.now()), source, target)
                    # os.remove(source)
                except Exception as e:
                    print('echo Failed to move %s' % source, str(datetime.now()), e, source, target)

        removeempty(src)


if __name__ == '__main__':
    # print(sys.argv[1], sys.argv[2])
    ingest(sys.argv[1], sys.argv[2])
    print('echo %s Ingestion Complete' % str(datetime.now()))


# import os
# import time
# import exifread

# def run(src, dst):
#     while True:
#         if not len(os.listdir(src)):
#             continue

#         files = os.listdir(src)
#         f = open('%s/%s' % (src, files[0]), 'rb')
#         tags = exifread.process_file(f)
#         print(tags.keys())

#         time.sleep(5)

# run('/Users/factoryreset/github/hhg/inbox', '/Users/factoryreset/github/hhg/outbox')


# import dateparser
# from PIL import Image

# def get_exif(filename):
#     image = Image.open('/Users/factoryreset/github/hhg/inbox/test.jpg')
#     image.verify()
#     return image._getexif()

# exif = get_exif('image.jpg')
# # print(exif)


# from PIL.ExifTags import TAGS

# def get_labeled_exif(exif):
#     labeled = {}
#     for (key, val) in exif.items():
#         labeled[TAGS.get(key)] = val

#     return labeled

# exif = get_exif('image.jpg')
# labeled = get_labeled_exif(exif)
# print(dateparser.parse(labeled['DateTimeOriginal']))