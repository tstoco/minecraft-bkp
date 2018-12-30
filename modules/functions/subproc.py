import time, logging, subprocess, os, datetime
from pathlib import Path

# Functions to manage SubProccess calls    

def check_output(args,splt=False,lines=False,position=None):
    # executes the check_output command
    # splt = true will return a list with the elements from the command run
    # lines = true will return a list with the lines from the command run
    # position will return the resquested element from the list
    try:        
        result = subprocess.check_output(args).decode('utf-8') # exceuting the command and storing its output            
        
        if splt: # if it should be splited 
            result = result.split() # split the result into a list            
        if lines:
            result = result.splitlines() # split the results into a list of lines  
        if not position == None:      
            result = result[position] # returning an specific line
        
        return result # returning the output after options have been applied
    except subprocess.SubprocessError as error:            
        raise  subprocess.SubprocessError(error) # raise an exception to be treated from the caller
                    
        
    