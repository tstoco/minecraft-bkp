import time, libtmux, logging

# Class to manage the tmux sessions

#TMUX Manual : http://man7.org/linux/man-pages/man1/tmux.1.html

# TMUX structure
# session (no name id=$0)
# ---- window (no name id=@0)
#--------pane (name=minecraft)
#--------pane (name=flask)
#--------pane (name=shell)

class Tmux:

    active_window = libtmux.Server().get_by_id('$0').select_window('@0')  # Select and set the window variable  
    
    #def __init__(self):
        # when instantiated a windown object is created 
        #self.window = libtmux.Server().get_by_id('$0').select_window('@0')        

    def set_pane_by_name(self,pane_name):        
        self.active_pane = self.active_window.find_where({"pane_title":"{0}".format(pane_name)})        

    def send_keys_to_pane(self,keys,pane_name):        
        # send a key command to the shell at the selected pane        
        self.set_pane_by_name(pane_name) # selecting a specific pane.                
        self.active_pane.cmd('send-keys','{0}'.format(keys)) # sending as .cmd() to avoid an extra space from the libtmux library.
        self.active_pane.enter() # execute the command        
        
        
