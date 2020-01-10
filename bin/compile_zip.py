#!/usr/bin/python3

import os
import os.path
import requests
import re
import shutil
import tempfile
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


def get_source_modules(repo,toolsdir,files=None):
    print("Retrieving",repo)
    url='https://github.com/linz/'+repo+'/zipball/master'
    r=requests.get(url)
    z=ZipFile(BytesIO(r.content))
    for n in z.namelist():
        if n.endswith('/'):
            continue
        m = re.match(r'^[\w\-]*(\/LINZ\/.+)$',n)
        if m:
            filepath=m.group(1)
            print("Extracting "+filepath)
            tgtfile=toolsdir+filepath
            path=os.path.dirname(tgtfile)
            if not os.path.isdir(path):
                os.makedirs(path)

            filename=os.path.basename(filepath)
            # Replace __init__.py with empty file to avoid package resources
            if filename == '__init__.py':
                with open(tgtfile,'wb') as tf:
                    pass
                continue
            # If selecting files then skip unmatched files
            if files and filename not in files:
                print("Omitting",filename)
                continue
            with open(tgtfile,'wb') as tf:
                tf.write(z.read(n))

def create_python_program(module,toolsdir,basemodule='LINZ.DeformationModel',progname=None):
    basedir=basemodule.replace('.','/')
    if not os.path.exists(toolsdir+'/'+basedir+'/'+module+'.py'):
        raise RuntimeError('Cannot find module {0} in LINZ.DeformationModel'.format(module))
    if not basemodule.startswith('LINZ.'):
        raise RuntimeError('Can only create programs from LINZ. modules')

    # Create path to LINZ directory, avoiding importing LINZ, as this
    # may not work if LINZ python modules already installed into python
    # distribution.
    basemodule=basemodule[5:]

    src='''#!/usr/bin/python3
        import sys
        import os.path
        sys.path.insert(1,os.path.join(os.path.dirname(os.path.abspath(__file__)),'LINZ'))
        from {basemodule} import {module}
        {module}.main()
        '''
    src=src.replace('{module}',module)
    src=src.replace('{basemodule}',basemodule)
    src=re.sub(r'^\s+','',src,flags=re.MULTILINE)
    progname=module if progname is None else progname
    progfile=toolsdir+'/'+progname+'.py'
    with open(progfile,'w') as pyf:
        pyf.write(src)
    os.chmod(progfile,0o755)

def build_tools( toolsdir ):
    if not os.path.isdir(toolsdir):
        os.makedirs(toolsdir)
    get_source_modules('python-linz-deformationmodel',toolsdir)
    get_source_modules('python-linz-geodetic',toolsdir,['Ellipsoid.py','ITRF.py'])
    get_source_modules('python-linz-geodeticgrid',toolsdir)
    create_python_program('CalcDeformation',toolsdir,progname='calcdeformation')
    create_python_program('ITRF_NZGD2000',toolsdir)
    create_python_program('NZGD2000_conversion_grid',toolsdir)
    create_python_program('LinzDefModelBin',toolsdir,
                          basemodule='LINZ.Geodetic',progname='build_linzdefmodel')

def add_tree_to_zip( basedir, zf ):
    for d,dirs,files in os.walk(basedir):
        zd=d
        if zd.startswith(basedir):
            zd=zd[len(basedir)+1:]
            if len(zd) > 0:
                zd=zd+'/'
        for f in files:
            if f == 'cache.h5':
                continue
            zf.write(os.path.join(d,f),zd+f)

basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tempdir=tempfile.mkdtemp()
try:
    print("Basedir:",basedir)
    print("Tempdir:",tempdir)
     
    toolssrc=tempdir+'/src'
    toolsdir=toolssrc+'/tools'
    if os.path.isdir(toolssrc):
        shutil.rmtree(toolssrc)
    build_tools(toolsdir)

    with open(basedir+'/src/VERSION') as vf:
        version=vf.readline().strip()

    if not re.match(r'^2\d\d\d[01]\d[0123]\d$',version):
        raise RuntimeError('Invalid version {0} - must be yyyymmdd'.format(version))

    zipfile='nzgd2000_deformation_'+version+'_full.zip'
    z=ZipFile(zipfile,'w',ZIP_DEFLATED)
    add_tree_to_zip(os.path.join(basedir,'src'),z)
    add_tree_to_zip(toolssrc,z)
finally:
    shutil.rmtree(tempdir)

