import sys, os, stat, time
import gzip
import tempfile, cStringIO
import urllib
import logging

if sys.platform == 'cygwin':
    local_repository = "/cygdrive/i/tarballs"
elif sys.platform == 'win32':    
    local_repository = "i:\tarballs"
else:
    local_repository = "/home/shared/tarballs"

python_ftp_url = "ftp://ftp.python.org/pub/python"
numeric_url = "http://prdownloads.sourceforge.net/numpy"
f2py_url = "http://cens.ioc.ee/projects/f2py2e/2.x"
scipy_url = "ftp://www.scipy.org/pub"
blas_url = "http://www.netlib.org/blas"
lapack_url = "http://www.netlib.org/lapack"
#atlas_url = "http://prdownloads.sourceforge.net/math-atlas"
atlas_url = "http://www.scipy.org/Members/eric"

#-----------------------------------------------------------------------------
# Generic installation class. 
# built to handle downloading/untarring/building/installing arbitrary software
#-----------------------------------------------------------------------------

class package_installation:    
    def __init__(self,version='', dst_dir = '.',
                 logger = None, python_exe='python'):
        #---------------------------------------------------------------------
        # These should be defined in sub-class before calling this
        # constructor
        #---------------------------------------------------------------------
        # 
        #self.package_url -- The name of the url where tarball can be found.
        #self.package_base_name -- The base name of the source tarball.
        #self.package_dir_name -- Top level directory of unpacked tarball
        #self.tarball_suffix -- usually tar.gz or .tgz
        #self.build_type -- 'make' or 'setup' for makefile or python setup file
        
        # Version of the software package.
        self.version = version

        # Only used by packages built with setup.py
        self.python_exe = python_exe
        
        # Directory where package is unpacked/built/installed
        self.dst_dir = os.path.abspath(dst_dir)        
        
        # make sure the destination exists
        dir_util.mkpath(self.dst_dir)
        
        if not logger:
            self.logger = logging
        else:
            self.logger = logger    

        # Construct any derived names built from the above names.
        self.init_names()
        
    def init_names(self):            
        self.package_dir = os.path.join(self.dst_dir,self.package_dir_name)
        self.tarball = self.package_base_name + '.' + self.tarball_suffix

    def get_source(self):
        """ Grab the source tarball from a repository.
        
            Try a local repository first.  If the file isn't found,
            grab it from an ftp site.
        """
        local_found = 0
        if self.local_source_up_to_date():
            try:
                self.get_source_local()
                local_found = 1                
            except DistutilsFileError:
                pass
        
        if not local_found:
            self.get_source_ftp()
                    
    def local_source_up_to_date(self):
        """ Hook to test whether a file found in the repository is current
        """
        return 1
        
    def get_source_local(self):
        """ Grab the requested tarball from a local repository of source
            tarballs.  If it doesn't exist, an error is raised.
        """
        file = os.path.join(local_repository,self.tarball)        
        dst_file = os.path.join(self.dst_dir,self.tarball)
        self.logger.info("Searching local repository for %s" % file)
        try:
            copy_file(file,dst_file,self.logger)
        except DistutilsFileError, msg:
            self.logger.info("Not found:",msg)
            raise
        
    def get_source_ftp(self):
        """ Grab requested tarball from a ftp site specified as a url.           
        """
        url = '/'.join([self.package_url,self.tarball])
     
        self.logger.info('Opening: %s' % url)
        f = urllib.urlopen(url)
        self.logger.info('Downloading: this may take a while')
        contents = f.read(-1)
        f.close()
        self.logger.info('Finished download (size=%d)' % len(contents))
     
        output_file = os.path.join(self.dst_dir,self.tarball)
        write_file(output_file,contents,self.logger)

        # Put file in local repository so we don't have to download it again.
        self.logger.info("Caching file in repository" )
        src_file = output_file
        repos_file = os.path.join(local_repository,self.tarball)        
        copy_file(src_file,repos_file,self.logger)

    def unpack_source(self,sub_dir = None):
        """ equivalent to 'tar -xzvf file' in the given sub_dir
        """       
        tarfile = os.path.join(self.dst_dir,self.tarball)
        old_dir = None
        
        # copy and move into sub directory if it is specified.
        if sub_dir:
            dst_dir = os.path.join(self.dst_dir,sub_dir)
            dst_file = os.path.join(dst_dir,self.tarball)
            copy_file(tarfile,dst_file)
            change_dir(dst_dir,self.logger)
        try:
            try:
                # occasionally the tarball is not zipped, try this first.
                untar_file(self.tarball,self.dst_dir,
                           self.logger,silent_failure=1)
            except:
                # otherwise, handle the fact that it is zipped        
                dst = os.path.join(self.dst_dir,'tmp.tar')        
                decompress_file(tarfile,dst,self.logger)                
                untar_file(dst,self.dst_dir,self.logger)
                remove_file(dst,self.logger)
        finally:
            if old_dir:
                unchange_dir(self.logger)

    def auto_configure(self):
        cmd = os.path.join('.','configure')
        text = run_command(cmd,self.package_dir,self.logger)

    def build_with_make(self):
        cmd = 'make'
        text = run_command(cmd,self.package_dir,self.logger)

    def install_with_make(self, prefix = None):
        if prefix is None:
            prefix = os.path.abspath(self.dst_dir)
        cmd = 'make install prefix=%s' % prefix
        text = run_command(cmd,self.package_dir,self.logger)

    def python_setup(self):
        cmd = self.python_exe + ' setup.py install'
        text = run_command(cmd,self.package_dir,self.logger)
    
    def _make(self,**kw):
        """ This generally needs to be overrridden in the derived class,
            but this will suffice for the standard configure/make process.            
        """
        self.get_source()
        self.unpack_source()
        self.auto_configure()
        self.build_with_make()
        self.install_with_make()

    def _setup(self):
        """ Build with Python setup script.
        """
        self.get_source()
        self.unpack_source()
        self.python_setup()

    def install(self):
        self.logger.info('####### Building:    %s' % self.package_base_name)
        self.logger.info('        Version:     %s' % self.version)
        self.logger.info('        Url:         %s' % self.package_url)
        self.logger.info('        Install dir: %s' % self.dst_dir)
        self.logger.info('        Package dir: %s' % self.package_dir)
        self.logger.info('        Suffix:      %s' % self.tarball_suffix)
        self.logger.info('        Build type:  %s' % self.build_type)
        if self.build_type == 'setup':
            self._setup()
        else:    
            self._make()
        self.logger.info('####### Finished Building: %s' % self.package_base_name)            
            
#-----------------------------------------------------------------------------
# Installation class for Python itself.
#-----------------------------------------------------------------------------
        
class python_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        # Specialization for Python.        
        self.package_base_name = 'Python-'+version
        self.package_dir_name = self.package_base_name
        self.package_url = '/'.join([python_ftp_url,version])
        self.tarball_suffix = 'tgz'
        self.build_type = 'make'
        
        package_installation.__init__(self,version,dst_dir,logger,python_exe)

    def write_install_config(self):    
        """ Make doesn't seem to install scripts in the correct places.
        
            Writing this to the python directory will solve the problem.
            [install_script]
            install-dir=<directory_name> 
        """
        text = "[install_scripts]\n"\
               "install-dir='%s'" % os.path.join(self.dst_dir,'bin')
        file = os.path.join(self.package_dir,'setup.cfg')               
        write_file(file,text,self.logger,mode='w')

    def install_with_make(self):
        """ Scripts were failing to install correctly, so a setuo.cfg
            file is written to force installation in the correct place.
        """
        self.write_install_config()
        package_installation.install_with_make(self)

    def get_exe_name(self):
        pyname = os.path.join('.','python')
        cmd = pyname + """ -c "import sys;print '%d.%d' % sys.version_info[:2]" """
        text = run_command(cmd,self.package_dir,self.logger)
        exe = os.path.join(self.dst_dir,'bin','python'+text)
        return exe

#-----------------------------------------------------------------------------
# Installation class for Blas.
#-----------------------------------------------------------------------------

class blas_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        # Specialization for for "slow" blas
        self.package_base_name = 'blas'
        self.package_dir_name = 'BLAS'
        self.package_url = blas_url
        self.tarball_suffix = 'tgz'
        self.build_type = 'make'
                
        self.platform = 'LINUX'
        package_installation.__init__(self,version,dst_dir,logger,python_exe)

    def unpack_source(self,subdir=None):
        """ Dag.  blas.tgz doesn't have directory information -- its
            just a tar ball of fortran source code.  untar it in the
            BLAS directory
        """
        package_installation.unpack_source(self,self.package_dir_name)
            
    def auto_configure(self):
        # nothing to do.
        pass
    def build_with_make(self, **kw):
        libname = 'blas_LINUX.a'
        cmd = 'g77 -funroll-all-loops -fno-f2c -O3 -c *.f;ar -cru %s' % libname
        text = run_command(cmd,self.package_dir,self.logger)

    def install_with_make(self, **kw):
        # not really using make -- we'll just copy the file over.        
        src_file = os.path.join(self.package_dir,'blas_%s.a' % self.platform)
        dst_file = os.path.join(self.dst_dir,'lib','libblas.a')
        self.logger.info("Installing blas")
        copy_file(src_file,dst_file,self.logger)

#-----------------------------------------------------------------------------
# Installation class for Lapack.
#-----------------------------------------------------------------------------

class lapack_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        # Specialization for Lapack 3.0 + updates        
        self.package_base_name = 'lapack'
        self.package_dir_name = 'LAPACK'
        self.package_url = lapack_url
        self.tarball_suffix = 'tgz'
        self.build_type = 'make'
        
        self.platform = 'LINUX'
        package_installation.__init__(self,version,dst_dir,logger,python_exe)

    def auto_configure(self):
        # perhaps this should actually override auto_conifgure
        # before make, we need to copy the appropriate setup file in.
        # should work anywhere g77 works...
        make_inc = 'make.inc.' + self.platform
        src_file = os.path.join(self.package_dir,'INSTALL',make_inc)
        dst_file = os.path.join(self.package_dir,'make.inc')
        copy_file(src_file,dst_file,self.logger)

    def build_with_make(self, **kw):
        cmd = 'make install lapacklib'
        text = run_command(cmd,self.package_dir,self.logger)

    def install_with_make(self, **kw):
        # not really using make -- we'll just copy the file over.
        src_file = os.path.join(self.package_dir,'lapack_%s.a' % self.platform)
        dst_file = os.path.join(self.dst_dir,'lib','liblapack.a')
        self.logger.info("Installing lapack")
        copy_file(src_file,dst_file,self.logger)
      
#-----------------------------------------------------------------------------
# Installation class for Numeric
#-----------------------------------------------------------------------------

class numeric_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        self.package_base_name = 'Numeric-'+version
        self.package_dir_name = self.package_base_name
        self.package_url = numeric_url
        self.tarball_suffix = 'tar.gz'
        self.build_type = 'setup'        

        package_installation.__init__(self,version,dst_dir,logger,python_exe)


#-----------------------------------------------------------------------------
# Installation class for f2py
#-----------------------------------------------------------------------------

class f2py_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        # Typical file format: F2PY-2.13.175-1250.tar.gz
        self.package_base_name = 'F2PY-'+version
        self.package_dir_name = self.package_base_name
        self.package_url = f2py_url
        self.tarball_suffix = 'tar.gz'
        self.build_type = 'setup'        
                
        package_installation.__init__(self,version,dst_dir,logger,python_exe)


#-----------------------------------------------------------------------------
# Installation class for Atlas.
# This is a binary install *NOT* a source install.
# The source install is a pain to automate.
#-----------------------------------------------------------------------------

class atlas_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        #self.package_base_name = 'atlas' + version
        #self.package_dir_name = 'ATLAS'
        self.package_base_name = 'atlas-RH7.1-PIII'
        self.package_dir_name = 'atlas'
        self.package_url = atlas_url
        self.tarball_suffix = 'tgz'
        self.build_type = 'make'        
        
        package_installation.__init__(self,version,dst_dir,logger,python_exe)

    def auto_configure(self,**kw):
        pass
    def build_with_make(self,**kw):
        pass
    def install_with_make(self, **kw):
        # just copy the tree over.
        dst = os.path.join(self.dst_dir,'lib','atlas')
        self.logger.info("Installing Atlas")
        copy_tree(self.package_dir,dst,self.logger)

#-----------------------------------------------------------------------------
# Installation class for scipy
#-----------------------------------------------------------------------------

class scipy_installation(package_installation):
    
    def __init__(self,version='', dst_dir = '.',logger=None,python_exe='python'):
        
        self.package_base_name = 'scipy_snapshot'
        self.package_dir_name = 'scipy'
        self.package_url = scipy_url
        self.tarball_suffix = 'tgz'
        self.build_type = 'setup'
        
        package_installation.__init__(self,version,dst_dir,logger,python_exe)
                    
    def local_source_up_to_date(self):
        """ Hook to test whether a file found in the repository is current
        """
        file = os.path.join(local_repository,self.tarball)
        up_to_date = 0
        try:
            file_time = os.stat(file)[stat.ST_MTIME]        
            fyear,fmonth,fday = time.localtime(file_time)[:3]
            year,month,day = time.localtime()[:3]
            if year == year and month == month and day == day:
                up_to_date = 1
                self.logger.info("Repository file up to date: %s" % file)
        except OSError, msg:
            pass
        return up_to_date
                
#-----------------------------------------------------------------------------
# Utilities
#-----------------------------------------------------------------------------


#if os.name == 'nt':
#    def exec_command(command):
#        """ not sure how to get exit status on nt. """
#        in_pipe,out_pipe = os.popen4(command)
#        in_pipe.close()
#        text = out_pipe.read()
#        return 0, text
#else:
#    import commands
#    exec_command = commands.getstatusoutput
   
# This may not work on Win98... The above stuff was to handle these machines.
