import urllib
import json
import urllib2
import optparse
import sys


DOWNLOAD_BASE = "https://raw.githubusercontent.com/fniephaus/alfred-workflow/master/%s"
FILE_LIST_URL = "https://api.github.com/repos/fniephaus/alfred-workflow/contents/workflow"


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-v', help='Verbose output', dest='verbose', default=False, action='store_true')
    (opts, args) = parser.parse_args()

    try:

        file_list = json.load(urllib2.urlopen(FILE_LIST_URL))

        file_downloader = urllib.URLopener()

        for wf_file in file_list:
            path = wf_file['path']

            if path.startswith('workflow/'):
                filename = path[len('workflow/'):]
                download_url = DOWNLOAD_BASE % path

                if opts.verbose:
                    print 'Updating %s...' % path
                
                try:
                    file_downloader.retrieve(download_url, filename)
                except IOError:
                    if opts.verbose:
                        print 'Could not download %s.' % path
                        print 'Aborting...'
                    sys.exit(1)
                except Exception:
                    if opts.verbose:
                        print 'An unknown error occurred while downloading %s.' % path
                        print 'Aborting...'
                    sys.exit(1)

        if opts.verbose:
            print """
======================================
Alfred-Workflow successfully updated!
======================================"""

    except urllib2.URLError:
        if opts.verbose:
            print 'Please check your Internet connection and try again.'
        sys.exit(1)
    except Exception:
        if opts.verbose:
            print 'An unknown error occurred.'
            print 'Aborting...'
        sys.exit(1)
