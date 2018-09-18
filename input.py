#!/usr/bin/python
import os

#call build_dependency.py
script = "build_dependency.py"
bld_log_file = str(os.getcwd) + "/log_files/jenkins_build_console_log_1.txt" 
command = 'python ' + script + ' ' + bld_log_file
