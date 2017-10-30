#                                                            _
# Ge push ds app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os

# import the Chris app superclass
from chrisapp.base import ChrisApp



class GePush(ChrisApp):
    """
    An app to push data of interest to GE cloud service.
    """
    AUTHORS         = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH        = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC        = os.path.basename(__file__)
    EXECSHELL       = 'python3'
    TITLE           = 'Ge Push'
    CATEGORY        = ''
    TYPE            = 'ds'
    DESCRIPTION     = 'An app to push data of interest to GE cloud service'
    DOCUMENTATION   = 'http://wiki'
    VERSION         = '0.1'
    LICENSE         = 'Opensource (MIT)'

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}
 
    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """
        self.add_argument('--prefix', dest='prefix', type=str, optional=False,
                           help='prefix string to be added to the GE cloud objects')
        self.add_argument('--contentType', dest='contentType', type=str, optional=False,
                           help='content type for the files')

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        # get GE cloud prefix
        prefix = options.prefix
        cont_type = options.contentType
        cmd = 'python {0} -c {1} -p {2} -t {3} -i {4}'.format('Agent17Upload.py',
                                                              'gehc-bch-sdk.config', prefix,
                                                              cont_type, options.inputdir)
        os.system(cmd)


# ENTRYPOINT
if __name__ == "__main__":
    app = GePush()
    app.launch()
