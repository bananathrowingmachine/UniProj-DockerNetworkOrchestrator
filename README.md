Important:
=
To allow it to run properly the python file expects to be in directory that includes itself and one more subdirectory, where this subdirectory contains all the docker files it needs. The repo will already be set up like this, so just make sure not to add any new directories, or pull everything into a directory that has directories already in it.

Additionally, this program heavily depends on running a lot of docker shell commands, which means that you must either run "sudo python3" or allow "sudo docker" to be passwordless.

Quick setup:
=
For a quick and easy setup, make sure the file structure remains unchanged, and then run the program. If the above 2 are correct, it will install all necessary packages then compose the containers.

More details on running the program:
=
This program is designed to essentially act as an extended command line interface. Therefore, it will attempt to run your commands then exit immediately once done and provide an exit message and exit code on what happened and if it was successful. Most needs should be met without requiring any command line arguments, however for more specific desires, run "-h" or "help" to run the help command and recieve more information on each available command, with subcommands of help going into greater detail on the main commands.

The only inputs the program will accept are up to 3 command line arguments, or in cases where the 1st or 2nd arguments are strings the program doesn't recognize, a [Y/N] input (where "Y" and "y" mean yes, anything else means no) that will ask the user if it wants to run the default option, if not, ask the user if it wants the relevant help page, and if not then the program will close. Occasionally, a third argument will be available to change how things works. If a 3rd argument is inputted that the program does not recognize, it will simply be ignored and act as if there was no third argument.

Additionally, the arguments are parsed in order, where each level has it's own command switch board, and the first unrecognized argument will flag that argument's switch board for help or running the default. Again, any unrecognized 3rd argument will simply be treated as if it was not there, even in cases where there is no third argument. Everything else beyond the 3rd command line argument will be ignored. 

Finally, giving 0 or 1 arguments will cause the program to run the default option. The default option for "help" is the main help page, the default option for "docker" verifies that docker is installed and running, and gets it installed and running if it isn't, the default option for "network" is to toggle the active path, and the default option for the entire program which can be called by giving it no arguments is to run "docker" default, and if everything was verified to be running, run "network" default. 

Assignment details are found at the link below:
=
link here

