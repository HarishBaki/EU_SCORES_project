#!/bin/bash
cd
# We are currently in the main directory. You can always come to the main directory by using cd ~/<directory name>
# Throughout this script, you will see ~ is used to direct the home directory, which is /home/hbaki in my case. If you are building WRF in a different folder, say Build_WRF, then replace ~ with complete location of Build_WRF.
# first create a Downloads folder and a Libraries folder. All the dependencies will be downloaded into the Downloads and build in the Libraries folder.
mkdir Downloads # This can be accessed from anywhere using cd ~/Downloads
mkdir Libraries # This can be accessed from anywhere using cd ~/Libraries
cd ~/Downloads
    wget -c https://zlib.net/fossils/zlib-1.2.11.tar.gz
    wget -c https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.5/src/hdf5-1.10.5.tar.gz
    wget -c https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-c-4.7.1.tar.gz
    wget -c https://github.com/Unidata/netcdf-fortran/archive/refs/tags/v4.5.1.tar.gz   # if the link doesn't work, download v4.5.1 directly.
    wget -c http://www.mpich.org/static/downloads/3.3.1/mpich-3.3.1.tar.gz
    wget -c https://download.sourceforge.net/libpng/libpng-1.6.37.tar.gz
    wget -c https://www.ece.uvic.ca/~frodo/jasper/software/jasper-1.900.1.zip
cd  # Always come to main home directory using this command.

# Compilers
export DIR=~/Libraries
export CC=gcc
export CXX=g++
export FC=gfortran
export F77=gfortran

# zlib
cd ~/Downloads
    tar -xvzf zlib-1.2.11.tar.gz
    cd zlib-1.2.11/
        ./configure --prefix=$DIR
        make
        make install
cd

# hdf5 library for netcdf4 functionality
cd ~/Downloads
    tar -xvzf hdf5-1.10.5.tar.gz
    cd hdf5-1.10.5
        ./configure --prefix=$DIR --with-zlib=$DIR --enable-hl --enable-fortran
        # make check # this command is commented, since Somehow, checking gives trouble.
        make install
cd

export HDF5=$DIR
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH

## Install NETCDF C Library
cd ~/Downloads
    tar -xvzf netcdf-c-4.7.1.tar.gz
    cd netcdf-c-4.7.1/
        export CPPFLAGS=-I$DIR/include
        export LDFLAGS=-L$DIR/lib
        ./configure --prefix=$DIR --disable-dap
        make check
        make install
cd

export PATH=$DIR/bin:$PATH
export NETCDF=$DIR

## NetCDF fortran library
cd ~/Downloads
    tar -xvzf netcdf-fortran-4.5.1.tar.gz
    cd netcdf-fortran-4.5.1
        export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH
        export CPPFLAGS=-I$DIR/include
        export LDFLAGS=-L$DIR/lib
        export LIBS="-lnetcdf -lhdf5_hl -lhdf5 -lz"
        ./configure --prefix=$DIR --disable-shared
        make check
        make install
cd

## MPICH
cd ~/Downloads
    tar -xvzf mpich-3.3.1.tar.gz
    cd mpich-3.3.1/
        ./configure --prefix=$DIR
        make
        make install
cd

export PATH=$DIR/bin:$PATH

# libpng
cd ~/Downloads
    export LDFLAGS=-L$DIR/lib
    export CPPFLAGS=-I$DIR/include
    tar -xvzf libpng-1.6.37.tar.gz
    cd libpng-1.6.37/
        ./configure --prefix=$DIR
        make
        make install
cd

# JasPer
cd ~/Downloads
    unzip jasper-1.900.1.zip
    cd jasper-1.900.1/
        autoreconf -i
        ./configure --prefix=$DIR
        make
        make install
cd
export JASPERLIB=$DIR/lib
export JASPERINC=$DIR/include

############################ WRF 4.4 #################################
## WRF v4.4
cd ~/Downloads
    wget -c https://github.com/wrf-model/WRF/archive/v4.4.tar.gz -O WRF-4.4.tar.gz
    tar -xvzf WRF-4.4.tar.gz -C ~/WRF   # This extracts the tar file into <main directory>/WRF/WRFV4.4
cd
cd ~/WRF/WRFV4.4/
    ./clean
    ./configure # 34, 1 for gfortran and distributed memory
    ./compile em_real >& log.compile
    #If you execute ls -ls main/*.exe , a successfull compilation will generate wrf.exe, real.exe, ndown.exe, and tc.exe.
cd
export WRF_DIR=~/WRF/WRFV4.4

## WPSV4.4
cd ~/Downloads
    wget -c https://github.com/wrf-model/WPS/archive/v4.4.tar.gz -O WPS-4.4.tar.gz
cd
cd ~/WRF/WPS-4.4
    ./configure #3
    ./compile
    #If you execute ls -ls main/*.exe , a successfull compilation will generate geogrid.exe, ungrib.exe, and metrgid.exe.
    
cd

# If you are installing WRF in a server, then install WPS along with it and also install the WPS in your local system. Then, create geo_em_d01.nc files in your local system, and the met_em_d0* files in the server. This really helps to save a lot of time in file trasfering.
######################### Cheers! #####################


