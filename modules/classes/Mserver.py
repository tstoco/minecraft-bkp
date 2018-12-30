import time, libtmux, logging, psutil
from .Tmux import Tmux
from .Files import Files

# Custom Modules
#from modules.classes import Mserver, Files
################

# Class to manage the Minecraft server commands

class Mserver(Tmux):

    pane = 'minecraft'    

    def say(self,msg):
        # method to send a message to players
        self.send_keys_to_pane('say {0}'.format(msg),self.pane)

    def is_running(self):
        is_running = False
        # psutil library is used to cycle through process and return TRUE/FALSE if find java 
        # which means the minecraft server is running
        for proc in psutil.process_iter(attrs=['pid','name']):
            if 'java' in proc.info['name']:                            
                is_running = True
        return is_running

    def stop(self,msg,seconds):
        # method to stop the server
        # msg = feedback to the players, why the server is being stopped
        # seconds = seconds to stop the server                
        self.say('**ATENCAO** - {0}'.format(msg)) 
        
        time.sleep(3) # small delay to start the countdown
        
        # counter to stop the server         
        while seconds >= 1:
            seconds -= 1
            self.say('O servidor esta parando em {0} segundo(s).'.format(seconds))          
            time.sleep(1)
        
        # Stoppping the server
        self.send_keys_to_pane('stop',self.pane)
    
    def start(self,svr_file_name):
        # method to start the server
        # start cmd
        cmd_start = ('java ' 
                    '-Xms12G ' 
                    '-Xmx12G '
                    '-XX:+UseG1GC '
                    '-XX:+UnlockExperimentalVMOptions '
                    '-XX:MaxGCPauseMillis=100 '
                    '-XX:+DisableExplicitGC '
                    '-XX:TargetSurvivorRatio=90 '
                    '-XX:G1NewSizePercent=50 '
                    '-XX:G1MaxNewSizePercent=80 '
                    '-XX:InitiatingHeapOccupancyPercent=10 '
                    '-XX:G1MixedGCLiveThresholdPercent=50 '
                    '-XX:+AggressiveOpts '
                    '-XX:+AlwaysPreTouch '
                    '-jar {0} -nogui'.format(svr_file_name))
        
        # Starting the server
        self.send_keys_to_pane('{0}'.format(cmd_start),self.pane)

    def save_all(self):
        # Method to save all the chuncks to files and backup the server folders
        self.send_keys_to_pane('save-all flush',self.pane)
    
    def backup(self,dst,src,files,live,svr_file_name):        
        # backup map         
        self.save_all() # saving the map from the memory to the disk
        time.sleep(5) # waiting 3 seconds
        self.say('esta iniciando o backup do mapa.')   

        # shut the server down if specified by the caller
        if not live:
            self.stop('vou parar pra tambem descarregar a memoria.',10)

        if files.copy(src,dst) == True: # if the copy is successful
            msg = 'fez o backup do mapa com sucesso.'
            bkp = True
        else: # if the copy fails
            msg = 'avisou o adminstrador que o backup falhou.'
            bkp = False
        
        # if the server is down it will be started
        if not self.is_running():
            self.start(svr_file_name)
        else: # if running pass the message to the players.
            self.say(msg)

        return bkp
        


        
        