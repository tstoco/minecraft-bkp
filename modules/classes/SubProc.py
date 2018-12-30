import time, logging, subprocess, os, datetime
from pathlib import Path

# Class to manage SubProccess calls

class SubProc:
    
    def __init__(self):
        self.error = None

    def check_output(self,args,splt=False,position=None):
        # executes the check_output command
        try:
            result = subprocess.check_output(args).decode('utf-8') # exceuting the command and storing its output            
            if splt: # if it should be splited 
                splited = result.split() # split the result into a list
                if not position == None:
                    return splited[position] # returning a specific value from the list
                else:
                    return splited # returning the whole list
            else:
                return result # returning the output wtihout any treatment
        except subprocess.SubprocessError as error:            
            self.error = 'SubProc().check_output() -> '+str(error) # logging the error and returning false            
            return False
                    
        
    