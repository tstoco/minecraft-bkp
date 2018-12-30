import time, logging, subprocess, os, datetime
from pathlib import Path
from .SubProc import SubProc
from ..functions.subproc import check_output

# Class to manage Files

class Files():

    subproc = SubProc() # subproccess object
    
    def __init__(self): 
        # sef explanatory variables
        self.path            = None
        self.file_name       = None
        self.obj_type        = None
        self.size            = None
        self.disk_size       = None
        self.used            = None
        self.available       = None
        self.folders_deleted = 0
        self.error           = None                   
        
    def path_exists(self,path):
        # check if a path exists
        if Path(path).exists():
            return True
        else:
            self.error = 'Path does not exist. from Files.py -> path_exists()'
            return False

    def format_size(self,str_size):
        # remove the MB from the and of the value and convert it to integer for future math    
        return int(str_size.replace('M',''))

    def info_cmd(self,path):
        # executes the cmd to get information from a file or folder
        # further improvement will be bring the df cmd from is_disk() to this function.
        if os.path.basename(path) != '' and os.path.isfile(path): # defining the object type              
            self.obj_type  = 'is_file'
            self.file_name = os.path.basename(path) # if is a file set file_name
        elif os.path.isdir(path):
            self.obj_type = 'is_folder'
        else:
            self.obj_type = 'is_disk'

        try:            
            du_output = subprocess.check_output(['du','-s', '--block-size=M', path]).split()[0].decode('utf-8') # du cmd returns information about a file or folder            
            self.size = self.format_size(du_output) # setting the obj size 
            
            df_output = subprocess.check_output(['df','--block-size=M', '--output=size,used,avail', path]).decode('utf-8') # execute a custom shell command to get disk information            
            dsk_vals = (df_output.splitlines()[1]).split() # strip junk info and get just size, used and available from the disk respectively.            
            for name,value in zip(['disk_size','used','available'],dsk_vals): # set object attributes from cmd_output                
                setattr(self,name,self.format_size(value))
                #setattr(self,name,self.format_size(value))                

            return True
        except subprocess.CalledProcessError as error:
            self.error = 'An error occured: {}'.format(error)
            return False         
    
    def cp_cmd(self,src,dst):
        # Create the backup folder and copy the contents
        bkp_folder = '{0}/bkp-{1}'.format(dst.path,(datetime.datetime.now()).strftime("%d-%m-%Y-%H.%M.%S")) 
        # getting current datetime and creating the BKP folder
        # now = (datetime.datetime.now()).strftime("%d-%m-%Y-%H.%M.%S") # getting current datetime.
        #dst.path = dst.path+'/bkp-'+now # creating BKP folder name and updating the object's  destination path
        os.mkdir(bkp_folder,mode=0o755) # creating BKP folder in the disk.

        try:
            args = ['cp']
            if src.obj_type == 'is_folder': # if it is a folder it will add -R to recursively copy the folder
                args.append('-R')
            args.extend([src.path,'-t',bkp_folder]) # -t copies arguments over                                    
            check_output(args)                
            return True        
        except subprocess.SubprocessError as error:                
            self.error = error  
            return False

    def count_dir(self,path):
        # counts how many files or folders there are in a directory 
        objects = 0
        for folder in os.scandir(path):
            objects += 1
        return objects

    def get_info(self,path):
        # return information ( size, space used, available ) from a folder, disk or file.
        
        if not self.path_exists(path): # if the path does not exist stop the function and return false
            self.error = 'File/Folder does not exist.'                       
            return False 
        
        self.path = path # Set the path of the object

        if self.info_cmd(path): # Runs the info_cmd method to get all the information from the the path
            return True

        return False

    def copy(self,src,dst):
        # method to copy files and folders 
                         
        free_space_needed = src.size + 20 # making sure to have at least 20MB free in the bkp media
        no_space_left = 'Replace the external media. There is not enough space. Disk Size ({1}MB) | Space needed ({0}MB)'.format(free_space_needed,dst.disk_size)
        
        #folders_deleted = 0
        
        while dst.available <= free_space_needed: # delete folders until get space available
            # if there is just one folder available and the disk_size is smaller than the space needed the operation fails.
            # the script could be changed here to optimize the use of space by comparing the size of the folder against the disk size
            if self.count_dir(dst.path) <= 1 and dst.disk_size < free_space_needed:
                self.error = no_space_left
                return False
            
            # deleting folders
            try:
                oldest_folder = check_output(['ls','-t', '-r', '-1', dst.path],True,False,0) # getting the oldest folder                
                check_output(['rm', '-R', dst.path+'/'+oldest_folder]) # deleting the oldest folder to make space to new bkps        
            except subprocess.SubprocessError as error:
                self.error = error # setting the error variable
                return False
            self.info_cmd(dst.path) # updating the class with the size after the copy          
            dst.available = self.available # updating the dst object.
            self.folders_deleted += 1  
            
        if dst.available > free_space_needed: # making sure that there is enough space to copy the folder
            self.cp_cmd(src,dst) # copy method
            self.info_cmd(dst.path) # updating the size after the copy
            dst.available = self.available # updating the object with the actual available size.        
            return True
        
        return False

        
        # SWITCh STATEMENT
        # https://jaxenter.com/implement-switch-case-statement-python-138315.html
