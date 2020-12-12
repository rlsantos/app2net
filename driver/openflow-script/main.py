"""
This is the main file, he manages every else
"""

from libs import run_command, run_command_w_output, download, cd, listdir, cur, mkdir, rename, rmdir, remove, popen, rmtree, clear
from config import BASE_DIR, NETAPPS_FOLDER, MENU_TEXT
import json, logging

def install():
    global FOLDER_NAME

    url = "https://github.com/FlyingWithJerome/SDNLoadBalancer/archive/master.zip"
    name = "load_balancer"

    # TODO fazer verificação da versão do Python (>=3.4) e da versão do OpenvSwitch (==2.7.0)
    requirements_commands = ["pip3.8 install ryu", ]

    for requirement in requirements_commands:
        run_command(requirement)

    #To Netapps Folder
    cd(NETAPPS_FOLDER)

    zipped = name+".zip"
    #Download Netapp
    download(url, zipped)

    #Unpacking file
    files = set(listdir())
    run_command('unzip '+ zipped)
    FOLDER_NAME = list(files-set(listdir()))
    remove(zipped)
    cd('..')

    print("Install finished. Please, configure.")

def initialize():
    global INSTALLED_NETAPPS
    global BASE

    # checking enviroment
    BASE = run_command_w_output('cd '+BASE_DIR+" && pwd")[:-1]
    cd(BASE)

    files_in_base = listdir()

    if not "netapps" in files_in_base:
        mkdir(NETAPPS_FOLDER)

    if not "mininam" in files_in_base:
        download('https://github.com/uccmisl/MiniNAM/archive/master.zip', 'mininam.zip')
        run_command('unzip mininam.zip')
        rename('MiniNAM-master', 'mininam')
        remove('mininam.zip')


    cd(NETAPPS_FOLDER)
    INSTALLED_NETAPPS = listdir()
    cd(BASE)

def delete(base, netapps_folder):
    logging.warning("\n\nAre you sure? This action can't be reversed. (S/n)\n")
    if input() == "S":
        print("Removing netapp")
        rmtree(base+"/"+netapps_folder+"SDNLoadBalancer-master/",)
    else:
        print('Aborted')


def stop():
    run_command("sudo killall -9 ryu-manager")
    print('Process stopped - Ryu controller')
    run_command("sudo killall -9 sudo")
    print('Process stopped - Mininet (Network)')

def start(base, netapps_folder):
    stop()

    lb_dir = base+'/'+netapps_folder+'SDNLoadBalancer-master/lb.py'
    lb_conf_dir = base+'/'+netapps_folder+'SDNLoadBalancer-master/lb_config.json'

    command_ryu = "xterm -e ryu-manager "+lb_dir+" --test-switch-dir "+lb_conf_dir
    command_mininam = "xterm -e sudo python "+base+'/'+'mininam/'+"MiniNAM.py --topo single,8 --mac --switch ovsk --controller remote"
    print(command_ryu, command_mininam)
    #running lb
    popen(command_ryu)
    print("Started - Ryu controller")

    #Running MiniNAM
    popen(command_mininam)
    print("Started - MiniNAM")

def configure(base, netapps_folder):
    dir = base+"/"+netapps_folder+"SDNLoadBalancer-master/lb_config.json"

    with open(dir) as file:
        confs = json.load(file)
    print("\n\n# # # #  Configure  # # # #")
    service_mac = input("\nThe current Service MAC value is "+str(confs['service_mac'])+". Would you like to change? (To keep the same value just press Enter)\n").replace(" ","")
    if service_mac != "":
        confs['service_mac'] = service_mac


    service_ips = input("The current Service IPs value is "+str(confs['service_ips'])+". Would you like to change? (To keep the same value just press Enter)\n").replace(" ", '')
    if service_ips != "":
        confs['service_ips'] = service_ips

    server_ips = input("The current Server IPs value is "+str(confs['server_ips'])+". Would you like to change? (To keep the same value just press Enter)\n").replace(" ", '')
    if server_ips != "":
        confs['server_ips'] = server_ips

    with open(dir, 'w') as outfile:
        json.dump(confs, outfile, indent=4)

    print("The settings have been saved")
    
initialize()


run = True
while run:
    clear()
    print(MENU_TEXT)
    option = input()

    #install
    if option == '1':
        install()

    #update settings
    elif option == '2':
        configure(BASE, NETAPPS_FOLDER)

    #Delete
    elif option == '3':
        delete(BASE, NETAPPS_FOLDER)

    #Deactivate
    elif option == '4':
        stop()

    #Activate
    elif option == '5':
        start(BASE, NETAPPS_FOLDER)

    #Exit
    elif option == '0':
        run = False

    #Outher input
    else:
        print("Invalid input")

