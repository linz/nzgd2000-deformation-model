# nzgd2000-deformation-model

**WARNING** Contents of this master branch of this repository may accessed by LINZ geodetic processes.  Ensure all data is correct before updating the master branch.

The NZGD2000 deformation model is used to transform coordinates 
between ITRF96 and NZGD2000.  

The deformation model comprises a set of .CSV files defining components such as 
the national velocity model, and the "patches" which represent deformation due
to earthquakes.  When it is published these are compiled into a single .zip file. 

The official releases are published at https://www.geodesy.linz.govt.nz/download/nzgd2000_deformation_model

The files and directory structure of the zip file are held in the .src directory
of this repository.  

The deformation model in the master branch will always reflect the current release
of the NZGD2000. Updated versions will be built in separate branches until they
are released.

The zip file contains [documentation](./src/documentation/NZGD2000DeformationModelFormat.pdf) 
describing the components of the model and how the deformation is
calculated from them for any given time or place.

The zip file also contains a reference implementation in python that 
can be used to calculate the deformation and apply it to coordinates.
This source code is in the [linz/python-linz-deformationmodel](https://github.com/linz/python-linz-deformationmodel) repository.  LINZ geodetic software such as SNAP and concord use a binary encoded
version of the deformation model.  The code for building this is in the
[linz/python-linz-geodeticgrid](https://github.com/linz/python-linz-geodeticgrid) repository.

## Maintenance

Future releases of the deformation model will be built in branches of this repository (eg 20170601) which will be pulled into the master branch when they are published, so that the master branch will hold the current published version of the deformation model.
