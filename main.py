import time, os, datetime, subprocess, sys, mysql.connector, logging, shutil, math
from pathlib import Path
from subprocess import Popen, PIPE
from flask import Flask, Response, Request
from apscheduler.schedulers.background import BackgroundScheduler
from modules.classes.Files import Files
from modules.functions.subproc import check_output

# CUSTOM
## Classes
from modules.classes import Mserver, Tmux 
## Functions

################

#apscheduler - Timezone
scheduler = BackgroundScheduler({'apscheduler.timezone':'Europe/London'}) # setting the timezone
scheduler.start()

# Config defined from file
app = Flask(__name__, instance_relative_config=True)
# Config file name
app.config.from_pyfile('minecheck.cfg')

logging.basicConfig(filename='logs.log',level=logging.WARNING,format='%(asctime)s %(message)s')

#WORKING CODE - APScheduler

def backup_server(): # BKP fucntion
    logging.warning('----------------BKP RUN AT: '+(datetime.datetime.now()).strftime("%d-%m-%Y %H:%M:%S") +'----------------')
    
    # Preventing the BKP if the server is locked to copy
    if app.config['LOCKCOPY']:
        logging.warning('SERVER LOCKED !! Contact the ADM.')
        logging.warning('----------------------------------------------------------------------------')
        return False
    
    app.config['LOCKCOPY'] = True # locking the server to avoid simoultaneous copies running at the same time
    mserver = Mserver.Mserver() # minecraft server object 
    src     = Files()           # source object
    dst     = Files()           # usb object
    files   = Files()           # object to handle the copy

    src.get_info(app.config['SVRMAPATH'])  # setting the source object    
    dst.get_info(app.config['SVRUSBPATH']) # setting the dest object

    # getting the day of the week to define if the server should be shutdown.
    #response += str((datetime.datetime.now()).strftime("%a"))
    live = True # define if the server should shutdown or not
    if (datetime.datetime.now()).strftime("%a") == app.config['DAYTOSTOP']:
        live = False

    if mserver.backup(dst,src,files,live,app.config['SVRFILENAME']):
        #success
        logging.warning('Status: SUCCESS !!')
        logging.warning('Folders Deleted: '+str(files.folders_deleted))        
    else:
        #error
        logging.warning('Folders Deleted: '+str(files.folders_deleted))
        logging.warning(str(files.error))
    app.config['LOCKCOPY'] = False
    logging.warning('----------------------------------------------------------------------------')

#SCHEDULER - Creating a cron event to run every day at 23:59 and the backup function
#            will have an argument to specify if the server should be stopped or not.
scheduler.add_job(backup_server,'cron', day_of_week=app.config['DAYS'], hour=app.config['HOUR'], minute=app.config['MIN'])

@app.route("/")
def index():  
    
    # getting the time now and formating it
    now = (datetime.datetime.now()).strftime("%d-%m-%Y %H:%M:%S") 
    response = 'Execution time : '+now+"<br>"

    #WORKING CODE - mySQL Connection
    """ try:      
        response = "<h1>SQL Connection SCRIPT | v1.0</h1><br> "
        # Connecting and selecting the DB        
        cnx = mysql.connector.connect(user=app.config['DBUSER'],
				                      password=app.config['DBPASSWORD'],
				                      host=app.config['DBHOST'],  
                                      database=app.config['DBDATABASE'])  
        # Setting a cursor
        cursor = cnx.cursor() 
        response += "<h2>Succeffuly connected !!</h2>"

    # treating any possible error with the connection
    except mysql.connector.Error as err:
  
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            response += "<h3>Something is wrong with your user name or password</h3>"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            response += "<h3>Database does not exist</h3>"
        else:
            response += "ERROR : "+str(err) 
  
        response += "<h1>Connection failed, contact the developer.</h1>"       

    else:
        response += "success!!"
    """
    ##############  
 
    #WORKIN CODE - Backup server
    """ if app.config['LOCKCOPY']:
        response += '<br>Server is locked. Contact the ADMIN.'
    else:
        response += '<br>BKP Started. LOCKCOPY: '+str(app.config['LOCKCOPY'])
        backup_server()
        response += '<br>BKP Completed. LOCKCOPY: '+str(app.config['LOCKCOPY']) """
    
    # print the jobs scheduled
    response += '<br>'+str(scheduler.print_jobs())
    
    # Display log file 
    logs = open('logs.log','r')    
    response += '<h2>Logs</h2>'
    for line in (logs.read()).splitlines():
        response += ('{br}{l}').format(br='<br>',l=line) 
    # Display log file 

    ##############    

    return Response(response),200 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", debug=True)

# APScheduler Documentation
# https://apscheduler.readthedocs.io/en/latest/userguide.html

# STRING ESCAPE UTILITY
#https://www.freeformatter.com/string-escaper.html

# CREATE pycache FOLDER in all the project folders.
# python3 -m compileall .

# du -s --block-size=K world_1.7.4/
# shell command to get the size of a folder

# AFTER A SYSTEM RESTART
 # 1) Create the TMUX structure
 # 2) Mount the USB into /home/minecraft/mineserver/ext_bkp (as minecraft user)
 #      id : command to check user id and groups the current user belongs to.
 # 3) Run the script -> be happy !=)

# FUTURE IMPLEMENTATIONS
# 1) Create bkps on the cloud : https://github.com/ncw/rclone
# 2) Send and email to the admin when a BKP fail or complete successfully
# 3) Add SQL functionality to log actions of the app
# 4) Create a frontend interface
# 5) code a init function  into Tmux class that should run a script to create the tmux session, windows and panels     
# 6) update my code to github
 