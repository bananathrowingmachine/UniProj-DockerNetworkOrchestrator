"""
A little program that can install and start a docker network setup, and then seamlessly orchastrate moving packets from the "top" route to the "bottom" route, using command line options.
Also yes, I do realize I went rather overboard with the command line interface.

Made by bananathrowingmachine, Apr 20, 2025
"""
import sys
import subprocess
import os

# Below is the section of functions for help and user input: 
# These assist in sending the exit codes and messages, handling unrecognized commands, running the help command, and verifying that docker is installed, running, and that the program has the ability to run sudo docker shell commands.
def exitMessage(msg: str, code = 0):
    """
    Adds the arrows to the exit message then terminates the program. Defaults to a successful termination.

    :param msg: The message to be broadcast.
    :param code: The exit code. 0 means all good and is the default.
    """
    print("-> " + msg + " <-")
    sys.exit(code)

def unrecognizedCommand(command: str):
    """
    Handles unrecognized commands, allowing users to see that command's help page, or run it's default option.

    :param command: The area that the unrecognized command was found (ie command = network if the unrecognized command was seemingly a network subcommand).
    """
    commandName = "<" + command + ">'s" if command != None else "the"
    print("Command not recognized. Would you like to run " + commandName + " default option? [Y/N]")
    inputStr = input().lower()
    if inputStr == "y":
        mainSwitch(command, None, None)
    else:
        commandName = "<" + command + ">" if command != None else "the program"
        print("Would you like help with " + commandName + "? [Y/N]")
        inputStr = input().lower()
        if inputStr == "y":
            helpOption(command, None)
        exitMessage(exitStrings["noChangeIssued"])

def helpOption(arg2: str, arg3: str):
    """
    Command switch for the help command. Includes everything needed for the help command, including details on all options, how they work, and how to use them.

    :param arg2: The second argument, used to get more in depth descriptions of <network>, <docker> or the default running of the program.
    :param arg3: The third argument, used to return the default running of <network> or <docker>.
    """
    equalsString = "======================================================"
    print(equalsString)

    if arg2 == "-d" or arg2 == "docker": # Docker help
        if arg3 == "-d" or arg3 == "default":
            print("The default mode will first determine if docker is installed in a way it understands. If not, it will run <docker install> automatically.")
            print("If docker is installed in a way the program expects, or after docker has finished installing, it will run <docker compose> to compose the containers.")
            print("The default behavior will never decompose the containers. You will need to run <docker decompose> to do that.")
        else:
            print("This command manages everything related to running docker. Running it without subcommands will cause the program to start building everything sequentially. Run <help docker default> to learn more.")
            print("All subcommands do specific things for further control, however most needs should be automatically detected.")
            print(equalsString)
            print("Below are the details on each sub command:")
            print("-> Use <-i> or <install> to install the docker program itself. Use <-f> or <force> to reinstall without checking if docker is already installed.")
            print("-> Use <-c> or <compose> to get docker to compose the docker containers. Use <-n> or <nocache> to ignore the cache when composing.")
            print("-> Use <-d> or <decompose> to get docker to decompose the docker containers.")

    elif arg2 == "-n" or arg2 == "network": # Network help
        if arg3 == "-d" or arg3 == "default":
            print("The default mode will determine which route the packets are currently flowing through and then reconfigure the routers to have them route through the other path.")
            print("It will essentially run <network route> then if it returns north run <network south>, otherwise <network north>.")
            print("The default option will never attempt to reconfigure the routers so that packets flow through the same path they were already flowing.")
        else:
            print("This command manages everything related to the orchestrator. Running it without subcommands will cause the program to toggle the active path. Run <help network default> to learn more.")
            print("All subcommands do specific things for further control, however most needs should be automatically detected.")
            print(equalsString)
            print("Below are the details on each sub command:")
            print("-> Use <-n> or <north> to have packets run through the northern route. Will let you know if the route was modified or not.")
            print("-> Use <-s> or <south> to have packets run through the southern route. Will let you know if the route was modified or not.")
            print("-> Use <-r> or <route> to determine which route packets are currently flowing through.")

    else: # Overall help
        if arg2 == "-h" or arg2 == "help":
            print("Gives helpful information about how to run this program, and all the commands and sub commands available.")
            print(equalsString)
            print("Below are the details on the sub command:")
            print("-> Use <-d> or <default> to learn about default behavior. Can either be used as an argument after <help> for overall default running states, or <help [command name]> for that command's specific default running states.")
        elif arg2 == "-d" or arg2 == "default":
            print("Running this program with no arguments will cause it to run in default mode. Default mode will verify that docker is running how it should be, and then toggle the path the packets are flowing through.")
            print("In the case that docker is not functional, it will attempt to install docker and then compose all of the containers.")
            print("Detecting if docker is running and if not installing and running it is the default <docker> behavior, and toggling the packet's path is the default <network> behavior.")
        elif arg2 != None:
            unrecognizedCommand("help")
            return
        else: 
            print("This program has 3 main command line arguments listed below, each with subcommands for further control. To use this program simply run it, all arguments are optional for improved control.")
            print("All commands in this program have both a <-n> and a <name> version, and any commands will be signified with <> on either side.")
            print("Using either version works, including different versions in the command and subcommand. Any caps also works. However do note order does matter.")
            print("Additionally, there are a few cases where a third argument is allowed. Inputting anything but that third argument will be ignored and the program will run as if there was no third argument.")
            print("Finally, most arguments will require the script to have elevated priviliges as it will execute <sudo docker> shell commands. The program will let you know if it doesn't have the priviliges it needs.")
            print(equalsString)
            print("Below are the basic details on each main command:")
            print("-> Use <-h> or <help> to bring up this menu. If you want more details on just a specific main command, including it's sub commands, run <help [command name]>.")
            print("If you want the details on the default behavior of each command, run append <-d> or <default> to your help command. <help default> will return full default specifications.")
            print("-> Use <-d> or <docker> to manage the docker containers. To start up everything as needed, run it without any subcommands.")
            print("-> Use <-n> or <network> to change route configurations. To simply toggle the route, run it without any subcommands.")
            print("-> Use no arguments to run completely normally. This will run the defaults set for <docker> and <network> when appropriate.")
            print(equalsString)
            print("After running each command, a message should appear saying what was run and if it succeeded. It will be bounded by -> and <-.")
    print(equalsString)

#
def dockerNotInstalled(notIstalled: bool):
    """
    Stops the user from running commands that require docker to be installed.

    :param notInstalled: Call this function with a boolean formula that determines if docker is installed.
    :return: A bool on if docker had to be started.
    """
    if notIstalled:
        print("Docker needs to be installed and running to run this command. Would you like to have it be automatically installed and started by the program? [Y/N]")
        inputStr = input().lower()
        if inputStr == "y":
            dockerCommand(None, None, True)
            return True
        exitMessage(exitStrings["noChangeIssued"])
    return False

def checkDockerPriviliges():
    """
    Verifies that the program can run sudo docker without needing a password. Returns if it can, terminates the program if it cannot.
    """
    sudoResult = subprocess.run('sudo -n docker --version', capture_output=True, text=True, shell=True)
    if sudoResult.returncode != 0:
        exitMessage("This command requires root privilages to run docker shell commands. Run the program again as sudo to quickly try again. " + exitStrings["fail"], sudoResult.returncode)

# Below are the functions for handling the commands that modify the docker setup.
# These include all commands related explicitly to docker including installation of docker and changing the router's path weights to reroute packets.
def dockerCommand(arg2: str, arg3: str, doNotTerminate: bool):
    """
    Command switch for the docker command. Allows users to install docker, and compose and decompose the container topology. 
    The default option will call <docker> subcommands to determine if docker is installed with the container topology running, or install and/or start the containers if not.

    :param arg2: The second argument, used to specify what <docker> subcommand the user wants. If left blank the best <docker> subcommands to run will be determined automatically and then run.
    :param arg3: The third argument, used for special cases of <docker install> and <docker compose>. Looks for the exact matching command or treats it as if it was blank.
    :param doNotTerminate: Used internally to keep the program from calling exitMessage and ending the program when called recursively by a default option.
    :return: Returns a bool representing if docker was installed and started before running the command to be used internally. Returns nothing if doNotTerminate is false.
    """
    checkInstalled = subprocess.run('dpkg -l | grep docker-ce-cli', capture_output=True, text=True, shell=True)
    if arg2 == "-i" or arg2 == "install": # Installing docker
        if checkInstalled.returncode == 0 and not (arg3 == "-f" or arg3 == "force"):
            if doNotTerminate: 
                return True
            exitMessage("Docker already installed. " + exitStrings["noChange"]) 
        installOutput = subprocess.run('./dockersetup', shell=True)
        if installOutput.returncode != 0:
            exitMessage("Docker failed to install. " + exitStrings["fail"], installOutput.returncode)
        if doNotTerminate: 
            return False
        addition = "re" if checkInstalled.returncode == 0 else ""
        exitMessage("Docker successfully " + addition + "installed. " + exitStrings["end"])

    if arg2 == None: # Automatically does everything that you'd probably want with <docker>.
        installed = dockerCommand("install", None, True)
        composed = dockerCommand("compose", None, True)
        if doNotTerminate: return installed and composed
        if installed:
            exitMessage("Docker was already installed. Containers have now been started. " + exitStrings["end"])
        if installed and composed:
            exitMessage("Docker was already installed with containers running. " + exitStrings["noChange"])
        exitMessage("Docker has been automatically installed and containers have been started. " + exitStrings["end"])

    if dockerNotInstalled(checkInstalled.returncode == 1): # Verifies that docker is installed before running the other commands. Allows user to install it automatically if not.
        exitMessage("Docker has been automatically installed and containers have been started. Rerun the program to run another command." + exitStrings["end"])
    checkDockerPriviliges()

    if arg2 == "-c" or arg2 == "compose": # Composing the containers
        checkComposed = subprocess.run('sudo docker ps', capture_output=True, text=True, shell=True)
        if len(checkComposed.stdout.splitlines()) != 1:
            if doNotTerminate: 
                return True
            exitMessage("Docker containers already running. " + exitStrings["noChange"])
        inputCommand = 'docker compose -p dn_topology up -d'
        if arg3 == "-n" or arg3 == "nocache":
            inputCommand = 'docker compose build --no-cache && ' + inputCommand
        output = subprocess.run('sudo ' + inputCommand, shell=True)
        if output.returncode != 0:
            exitMessage("Docker failed to compose. " + exitStrings["fail"], output.returncode)
        if doNotTerminate: 
            return False
        exitMessage("Docker containers successfully composed. " + exitStrings["end"])

    if arg2 == "-d" or arg2 == "decompose": # Decomposing the containers
        checkComposed = subprocess.run('sudo docker ps', capture_output=True, text=True, shell=True)
        if len(checkComposed.stdout.splitlines()) == 1:
            exitMessage("No docker containers running. " + exitStrings["noChange"])
        output = subprocess.run('sudo docker compose -p dn_topology down', shell=True)
        if output.returncode != 0:
            exitMessage("Docker failed to decompose. " + exitStrings["fail"], output.returncode)
        exitMessage("Docker containers successfully decomposed. " + exitStrings["end"])

    # For unrecognized subcommands. Asks if the default or help is wanted before terminating.
    unrecognizedCommand("docker")

def orchestratorCommand(arg2: str, doNotTerminate: bool):
    """
    Command switch for the network command. Allows users to determine what route the packets are able to flow through currently, and change it manually. 
    The default option will call <network> subcommands to toggle the active route.

    :param arg2: The second argument, used to specify what <network> subcommand the user wants. If left blank the best <network> subcommands to run will automatically be determined and then run.
    :param doNotTerminate: Used internally to keep the program from calling exitMessage and ending the program when called recursively by a default option.
    :return: Returns a bool representing the route to be used internally. Returns nothing if doNotTerminate is false.
    """
    if not doNotTerminate: # Verifies that docker is installed, running before running the other commands. Allows user to install it automatically if not. Skipped if doNotTerminate is True as that can only True if called internally.
        checkInstalled = subprocess.run('dpkg -l | grep docker-ce-cli', capture_output=True, text=True, shell=True)
        if dockerNotInstalled(checkInstalled.returncode == 1):
            print("Docker has been automatically installed and containers have been started. Your command will now continue executing.")
            route = "north" if orchestratorCommand(arg2, True) else "south" # doNotTerminate only keeps route from executing, so this will only get reached if route was called.
            exitMessage("Packets are currently flowing through the " + route + "ern route. " + exitStrings["end"])
        else:
            checkDockerPriviliges()
            checkComposed = subprocess.run('sudo docker ps', capture_output=True, text=True, shell=True)
            if len(checkComposed.stdout.splitlines()) == 1:
                print("Docker needs to be running to run this command. Would you like to have it get turned on by the program? [Y/N]")
                inputStr = input().lower()
                if inputStr == "y":
                    dockerCommand("compose", None, True)
                    print("Docker containers successfully composed. Your command will now continue executing.")
                    route = "north" if orchestratorCommand(arg2, True) else "south" # doNotTerminate only keeps route from executing, so this will only get reached if route was called.
                    exitMessage("Packets are currently flowing through the " + route + "ern route. " + exitStrings["end"])
                else:
                    exitMessage(exitStrings["noChangeIssued"])

    if arg2 == "-r" or arg2 == "route": # Determines which route is currently being used.
        checkComposed = subprocess.run("sudo docker exec -it dn_topology-r4-1 vtysh -c 'show running' | grep 'ip ospf cost'", capture_output=True, text=True, shell=True)
        output = int(checkComposed.stdout.split(' ')[4]) == 3 # North route is True, South route is False. Therefore, since r2 will always have weights of 2, r4 having weights of 3 means North route, and 1 means South route.
        if doNotTerminate:
            return output
        route = "north" if output else "south"
        exitMessage("Packets will currently flow through the " + route + "ern route. " + exitStrings["noChangeIssued"])

    if arg2 == "-n" or arg2 == "north": # Setting the north route as the packet flow route (by making r4 more expensive than r2).
        if (not doNotTerminate) and orchestratorCommand("route", True):
            exitMessage("Packets are currently able to flow through the northern route. " + exitStrings["noChange"])
        output1 = subprocess.run("sudo docker exec -it dn_topology-r4-1 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 3' -c 'end'", capture_output=True, text=True, shell=True)
        output2 = subprocess.run("sudo docker exec -it dn_topology-r4-1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 3' -c 'end'", capture_output=True, text=True, shell=True)
        if output1.returncode != 0 or output2.returncode != 0:
            exitMessage("Unable to modify the OSPF cost of the routes. " + exitStrings["fail"])
        exitMessage("OSPF cost of the routes modified. Packets will now flow through the northern route. " + exitStrings["end"])
        
    if arg2 == "-s" or arg2 == "south": # Setting the south route as the packet flow route (by making r4 less expensive than r2).
        if (not doNotTerminate) and (not orchestratorCommand("route", True)):
            exitMessage("Packets are currently able to flow through the southern route. " + exitStrings["noChange"])
        output1 = subprocess.run("sudo docker exec -it dn_topology-r4-1 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf cost 1' -c 'end'", capture_output=True, text=True, shell=True)
        output2 = subprocess.run("sudo docker exec -it dn_topology-r4-1 vtysh -c 'configure terminal' -c 'interface eth1' -c 'ip ospf cost 1' -c 'end'", capture_output=True, text=True, shell=True)
        if output1.returncode != 0 or output2.returncode != 0:
            exitMessage("Unable to modify the OSPF cost of the routes. " + exitStrings["fail"])
        exitMessage("OSPF cost of the routes modified. Packets will now flow through the southern route. " + exitStrings["end"])

    if arg2 == None: # Automatically does everything that you'd probably want with <network>.
        orchestratorCommand("south" if orchestratorCommand("route", True) else "north", True)
        
    # For unrecognized subcommands. Asks if the default or help is wanted before terminating.
    unrecognizedCommand("network")

# Below are the functions related to the main functionality of the program.
# These include the main command switch board, as well as argument parsing and global variable setup.
def mainSwitch(arg1: str, arg2: str, arg3: str):
    """
    Command switch for the main commands. Best thought of as the main function. 

    :param arg1: The first argument, for the 3 command groups of <help>, <network>, and <docker>. If left blank, the program will automatically verify that docker is running, start it if it is not, or toggle the active route if it is.
    :param arg2: The second argument, used for subcommands of <help>, <network>, and <docker>. If left blank, the best subcommands to run will be determined and then run.
    :param arg3: The third argument, occasionally used by <help> and <docker. If not in a form described by <help>, it will be treated as blank and ignored.
    """
    if arg1 == "-h" or arg1 == "help": 
        helpOption(arg2, arg3)
        exitMessage(exitStrings["noChangeIssued"])
    if arg1 == "-n" or arg1 == "network": 
        orchestratorCommand(arg2, False)
    if arg1 == "-d" or arg1 == "docker": 
        dockerCommand(arg2, arg3, False)
    if arg1 == None:
        if dockerCommand(None, None, True):
            orchestratorCommand(None, True)
        exitMessage("The docker setup has been created and started. Rerun this program to toggle which route the packets flow through. " + exitStrings["end"])
    
    # For unrecognized commands. Asks if the default or help is wanted before terminating.
    unrecognizedCommand(None)
    exitMessage(exitStrings["noChangeIssued"])

"""
Program setup. Verifies docker can be run without password, creates the exit string variables for internal use, 
and changes the programs directory to the first directory it shares a directory with (which is how my current setup is structured).
"""
exitStrings = {}
exitStrings["end"] = "Program closing."
exitStrings["noChange"] = "Nothing was changed. " + exitStrings["end"]
exitStrings["noChangeIssued"] = "No modifying instructions issued. " + exitStrings["noChange"]
exitStrings["fail"] = "Program failed. Terminating."
try:
    filePath = subprocess.run('ls -d */', capture_output=True, text=True, shell=True).stdout
    filePath = filePath.replace('\n','').replace('/','')
    os.chdir(filePath)
except:
    exitMessage("Could not find docker config files. " + exitStrings["fail"])

"""
Essentially the main method. Prases all the arguments in one line, and sends them to the mainSwitch where things really get started.
"""
mainSwitch(sys.argv[1].lower() if len(sys.argv) > 1 else None, sys.argv[2].lower() if len(sys.argv) > 2 else None, sys.argv[3].lower() if len(sys.argv) > 3 else None)
