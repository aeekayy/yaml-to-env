#!/usr/bin/env python3

##############################################
## 
## Veritone DevOps Team - devops@veritone.com
##
##############################################
## 
## Take a yaml and set the contents of the 
## YAML to environment variables 
## so that a process or program can consume
## those variables 
##
##############################################

# Imports
import argparse
import os
import re
import sys
import yaml

def parseArgs(): 
    parser = argparse.ArgumentParser(description='YAML to OS environment variable parser')
    parser.add_argument('-f', '--file', default='manifest.yaml', type=str, action='store', help='The filename of the manifest to be read.')
    parser.add_argument('-s', '--script', default='setEnv.sh', type=str, action='store', help='The output script to create with the environment variables written to it.')
    return parser.parse_args()

## 
## Create a list from a dictionary
## that can be parsed and used
## to create environment variables
def read_dict(dictionary): 
    write_list = []

    if(isinstance(dictionary, dict)):
        for key in dictionary: 
            write_list.append(key)
            if(not isinstance(dictionary[key], str)):
                write_list += read_dict(dictionary[key])
    else:
        # recursive function
        write_list.append(str(dictionary))
    return write_list
##
## Create an OS variable from
## string and list of items
def create_os_var(prefix, string, listItems):
    listItems.insert(0,prefix)
    listItems.insert(1,string)
    value = listItems.pop()
    varName = "_".join(listItems)
    varName = re.sub(r'\.|-', '_', varName)
    return("%s=\"%s\"" % (varName.upper(),value))

def main():
    # Parse the arguments
    arguments = parseArgs()
    yamlFile = 'manifest.yaml'
    bashScript = 'setEnv.sh'
    bashOutput = ["#!/bin/bash"]

    if arguments.file != None:
        yamlFile = arguments.file
    if arguments.script != None:
        bashScript = arguments.script

    ## FASTCORE_IMPORT_FAILED 
    ## variable for the OS to know 
    ## whether or not the import of the 
    ## YAML is successful or not 
    os.environ["FASTCORE_IMPORT_FAILED"] = "false"

    ## Open the yaml and iterate
    ## Though the yaml to grab all of the variables
    ## assign all values to environment variables
    try:
        bash = open(bashScript, "w")
        with open(yamlFile) as file:
            fastcore = yaml.load(file,Loader=yaml.FullLoader)

            for key,item in fastcore.items():
                for subkey in item:
                    bashOutput.append(create_os_var(key, subkey, read_dict(item[subkey])))
        # Write to bash script file
        bash = open(bashScript, "w")
        bash.write("\n".join(bashOutput))
        bash.close()
        print("The file %s has been created!" % bashScript)
    except Exception as e:
        print("Could not open the file %s" % yamlFile)
        print("Error: %s" % e)
        sys.exit(1)
    finally:
        bashOutput.append("FASTCORE_IMPORT_FAILED=true")
        bash = open(bashScript, "w")
        bash.write("\n".join(bashOutput))
        bash.close()

if __name__ == '__main__':
    main()
