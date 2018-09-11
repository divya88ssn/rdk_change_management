#/home/divyaven/bin/python

#import libraries

#global variables
comp_list_dict = {} #list of components in this build
comp_dep_list_dict = {} #dictionary that stores (component(str),dependency_list) as key and value respectively

#build dependency graph from component build_dependency key value list
def build_dependency_graph():
	if not (comp_dep_list_dict):
        	print "Error: component build_dependency key value list is empty \n"
	else:
		print "ok\n"

#called from main()
def get_build_info(ip_file):
	line_marker_1 = False
	line_marker_2 = False
	line_cnt = 10
	with open(ip_file) as bldOutput:
		for line in bldOutput:
               		if (line_marker_1 and line_marker_2):
                   		line_cnt = line_cnt - 1
                   		if (line_cnt <= 8 and line_cnt > 0):
                       			if (line_cnt == 8):
                           			print "\n"
                           			print "Build info :\n"
                           			print "============\n"
                       			if (line_cnt == 3):
                           			jenkins_bld_num = (line.split("=")[1]).strip()
                       			if (line_cnt == 4):
                           			jenkins_bld_job_name = (line.split("=")[1]).strip()
                       			print line
               		if (line_marker_1):
                   		if ("======================================" in line):
                       			line_marker_2 = True
               		if ("INFO Build order:" in line):
                   		line_marker_1 = True

	jenkins_build_url = "https://jenkins.ccp.xcal.tv/jenkins/job/"+jenkins_bld_job_name+"/"+jenkins_bld_num+"/consoleText"
	print "Jenkins build url for the ip_file is " + jenkins_build_url + "\n"

#called from parse_build_order
def build_comp_dep_keyval_dict(component, dep_list):
	ret = True
	if (component):
		if (dep_list):
			if not (comp_dep_list_dict.has_key(component)):
                   		comp_dep_list_dict.update({component:dep_list})
               		else:
                		print "Duplicate component parsed error \n"
                   		ret = False
		else:
        		print "The dependency list for " + component + " is empty\n"
	else:
        	print "The " + component + "recieved is empty string error \n"
        	ret = False
	return ret

#called from parse_build_order
def build_comp_list(component,index):
	ret = True
	if (component and index):
		if not (comp_list_dict.has_key(component)):
			comp_list_dict.update({component:index})
		else:
			print "Error: Duplicate component passed to build_comp_list routine\n"
			ret = False
	else:
		print "Error: Component or index input is null \n"
		ret = False
	return ret

#called form main()
def parse_build_order(ip_file):
	parse_list_order = False
       	ret = True #success
       	index = 0
       	with open(ip_file) as bldOutput:
        	for line in bldOutput:
               		if ("==============================================" in line):
                   		parse_list_order = False

               		if (parse_list_order and ret):
                   		parse_line = line.split(" ",5)
                   		if (len(parse_line) > 5):
                       			component_with_dep_list = parse_line[5]
                       			component = component_with_dep_list.split(" ")[0]
                       			#build component list
                       			index = index + 1
                       			ret = build_comp_list(component,index)
                       			#returns False on null or duplicate component string
                       			if not (ret):
                           			return ret
                       			#parse component dependency list
                       			null_dependency_chk = component_with_dep_list.split("[")
                       			if (len(null_dependency_chk) > 1):
                           			tmp_dep_list = component_with_dep_list.split("[")[-1]
                           			dependency_list = tmp_dep_list.split("]")[0]
                           			dep_list = dependency_list.split(",")
                           			ret = build_comp_dep_keyval_dict(component, dep_list)
                       			else:
                           			dep_list = ""
                           			ret = build_comp_dep_keyval_dict(component, dep_list)
               		else:
                   		if ("INFO Build order:" in line):
                       			parse_list_order = True
	return ret

#called form main()
def get_num_of_wanted_lines(ip_file):
	start_count = False
	stop_count =  False
	cnt = 0
	with open(ip_file) as bldOutput:
		for line in bldOutput:
               		#get start of build dependency listing
               		if ("INFO Build order:" in line):
                   		start_count = True
               		if ("INFO Packaging Successfull" in line):
                   		stop_count = True
               		if (start_count and not stop_count):
                   		cnt = cnt + 1
	return cnt

def main():
	ip_file = "jenkins_build_console_log.txt"
	num_lines = get_num_of_wanted_lines(ip_file)
	get_build_info(ip_file)
	print "\n"
	print "The number of wanted lines from " + ip_file + " is " + str(num_lines) + "\n"
	#return_value = parse_build_order(ip_file)
	#if (return_value):
		#print "Successfully built component dependency key value pair for this build\n"
		#print str(comp_list) + "\n"
		#build_dependency_graph()
	#else:
		#print "Error: parsing build order and building component dependency key value pair list\n"

if __name__ == "__main__":
	main()
