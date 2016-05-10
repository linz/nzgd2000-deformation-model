#!/usr/bin/python

import os
import os.path
import requests
import re
import shutil
import tempfile
from StringIO import StringIO
from zipfile import ZipFile


def get_source_modules(repo,toolsdir):
    print "Retrieving",repo
    url='https://github.com/linz/'+repo+'/zipball/master'
    r=requests.get(url)
    z=ZipFile(StringIO(r.content))
    for n in z.namelist():
        if n.endswith('/'):
            continue
        m = re.match(r'^[\w\-]*(\/LINZ\/.+)$',n)
        if m:
            print "Extracting "+m.group(1)
            tgtfile=toolsdir+m.group(1)
            path=os.path.dirname(tgtfile)
            if not os.path.isdir(path):
                os.makedirs(path)
            with open(tgtfile,'wb') as tf:
                tf.write(z.read(n))

def create_python_program(module,toolsdir):
    if not os.path.exists(toolsdir+'/LINZ/DeformationModel/'+module+'.py'):
        raise RuntimeError('Cannot find module {0} in LINZ.DeformationModel'.format(module))
    src='''#!/bin/python
        import sys
        import os.path
        sys.path.insert(0,os.path.dirname(__file__))
        from LINZ.DeformationModel import {module}
        {module}.main()
        '''
    src=src.replace('{module}',module)
    src=re.sub(r'^\s+','',src,flags=re.MULTILINE)
    with open(toolsdir+'/'+module+'.py','w') as pyf:
        pyf.write(src)

def build_tools( toolsdir ):
    if not os.path.isdir(toolsdir):
        os.makedirs(toolsdir)
    get_source_modules('python-linz-deformationmodel',toolsdir)
    get_source_modules('python-linz-geodetic',toolsdir)
    create_python_program('CalcDeformation',toolsdir)
    create_python_program('ITRF_NZGD2000',toolsdir)
    create_python_program('NZGD2000_conversion_grid',toolsdir)

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
    print "Basedir:",basedir
    print "Tempdir:",tempdir
     
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
    z=ZipFile(zipfile,'w')
    add_tree_to_zip(os.path.join(basedir,'src'),z)
    add_tree_to_zip(toolssrc,z)
finally:
    shutil.rmtree(tempdir)

