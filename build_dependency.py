#/home/divyaven/bin/python

#import libraries
import sys

#global variables
comp_index_list_dict = {} 	# dictionary that stores (component(str),index(int))
comp_dep_list_dict = {} 	#dictionary that stores (component(str),dependency_list) as key and value respectively
comp_list = [] 			#indexable list of components
dep_comp_list_dict = {} 	#dictionary that stores (component(str), list of components that depend on this component)
path_rev_dict = {} 		#dictionary that stores (component path(str), component revision id(str))
path_branch_dict = {} 		#dictionary that stores (component path(str), branch(str))
path_list =[]			#list of component repo paths
path_comp_map_dict = {}
dummy_list = []			#list of components whose path end with /generic

#called from main
def parse_comp_revisions(ip_file):
	ret = True
	start_parsing = False
	stop_parsing = False
	count = 0
	with open(ip_file) as bldOutput:
		for line in bldOutput:
			if (start_parsing and not stop_parsing):
				#get branch and component path
				split_list = line.split("@")
				if (len(split_list) >= 2):
					branch = split_list[1].strip().split(":")[0].strip()
					#print "Component branch is " + branch + "\n"
					path = split_list[0].strip().split(":")[-1].strip()
					#print "Component path is " + path  + "\n"
					if (path):
						is_generic = path.split("/")[-1].strip()
						if (is_generic == "generic"):
							path_of_comp = path.split("/")[-2].strip()
							dummy_list.append(path_of_comp)
							path_comp_map_dict.update({path_of_comp:path})
						path_list.append(path)
						if not (path_branch_dict.has_key(path)):
							path_branch_dict.update({path:branch})
				#get component revision
				split_list = line.split("|")
				if (len(split_list) >= 2):
					rev = split_list[0].strip().split(":")[-1].strip()
					count = count + 1
					#print "Rev is " + rev + "\n"
					if (path):
						if not (path_rev_dict.has_key(path)):
							path_rev_dict.update({path:rev})

				#print "-----------------------------------------------\n"

			if ("REVISION HISTORY FOR EXTERNALS" in line):
				start_parsing = True
			if ("----------------------------------------------" in line):
				stop_parsing = True

	print "Number of lines processed are " + str(count) + "\n"
	return ret

#called from main
def display_dependent_components(comp):
	ret = True
	if (comp):
		if (dep_comp_list_dict.has_key(comp)):
			print "Components dependent on " + comp + " for build are " + str(dep_comp_list_dict.get(comp)) + "\n"
		else:
			ret = False
	else:
	  ret = False
	return ret

#called from build_dependency_graph()
def parse_dep_list(comp, dep_list):
	ret = True
	if (comp and dep_list):
		index_val = 0
		if (comp_index_list_dict.has_key(comp)):
			#sdk has index val of 1 in this dict
			comp_index = comp_index_list_dict.get(comp)
			for val in dep_list:
				val = val.strip()
				index = comp_index_list_dict.get(val)
				if (index > comp_index):
					print "Error: Component " + comp + " has a dependency that will be built after this component\n"
					return False
				else:
					#now update dep_comp_list_dict for 'val'
					if (dep_comp_list_dict.has_key(val)):
						(dep_comp_list_dict.get(val)).append(comp)
					#else:
						#print "Warning: for " + comp + " dependency " + val + " not in dep_comp_list_dict\n"
						#print "Warning: The index of " + val + " is " + str(index) + "\n"
		else:
			print "Error: Component not in comp index dictionary\n"
			ret = False
	else:
		print "Error: Null inputs to this argument\n"
		ret = False
	return ret

#called from main
#build dependency graph from component build_dependency key value list
def build_dependency_graph():
	print "building dependency graph for this build\n"
	ret = True
	if not (comp_dep_list_dict):
		print "Error: component build dependency key value list is empty \n"
		ret = False
	else:
		count = len(comp_list)
		if (count > 0):
			#iterate through component list and check list order of dependencies
			itr = 0
			while (itr <= count - 1):
				comp = comp_list[itr]
				#initialize the dependent components list for this comp as empty
				if not (dep_comp_list_dict.has_key(comp)):
					dependent_comps = []
					dep_comp_list_dict.update({comp:dependent_comps})
				else:
					print "Error: Component being examined is duplicate of an alreday existing entry\n"
					ret = False
					return ret
				#get the dependency list for this component
				#components with no dependencies wont be in this dict
				if (comp_dep_list_dict.has_key(comp)):
					dep_list = comp_dep_list_dict.get(comp)
					#print comp + " has dependencies: " + str(dep_list) + "\n"
					#parse dependency list to build dependency graph
					ret = parse_dep_list(comp,dep_list)
					if not (ret):
						print "Error: Exiting building dependency graph while processing " + comp + "\n"
						return ret
				else:
					print comp + " has no dependencies: root component\n"
				itr = itr + 1
		else:
			print "Error: Empty component list \n"
			ret = False
	
	return ret

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
		#else:
        	#print "The dependency list for " + component + " is empty\n"
	else:
        	print "The " + component + "recieved is empty string error \n"
        	ret = False
	return ret

#called from parse_build_order
def build_comp_list(component, index):
	ret = True
	if (component and index):
		if not (comp_index_list_dict.has_key(component)):
			comp_index_list_dict.update({component:index})
		else:
			print "Error: Duplicate component passed to build_comp_list routine\n"
			ret = False
		comp_list.append(component)
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
	
	#for arg in sys.argv[1:]:
		#print "Inside build_dependency.py " + arg + "\n"
	ip_file = "jenkins_build_console_log_3.txt"
	#num_lines = get_num_of_wanted_lines(ip_file)
	get_build_info(ip_file)
	#print "\n"
	#print "The number of wanted lines from " + ip_file + " is " + str(num_lines) + "\n"
	return_value = parse_build_order(ip_file)
	if (return_value):
		print "Successfully built component dependency key value pair for this build\n"
		print "The components for this build are " + str(comp_list) + "\n"
		print "The number of components listed in the build order are " + str(len(comp_list)) + "\n"
		ret = build_dependency_graph()
		if (ret):
			print "Successfully built dependency graph for the given build\n"
			comp = "video-analytics"
			print comp + " has dependency on " + str(comp_dep_list_dict[comp]) + "\n"
			ret = display_dependent_components(comp)
			if not(ret):
				print "Error: Displaying dependent components for " + comp + "\n"
	else:
		print "Error: parsing build order and building component dependency key value pair list\n"
	ret = parse_comp_revisions(ip_file)
	if (ret):
		print "Successfully parsed gerrit revision ids for the components in this build\n"
		path = path_comp_map_dict.get("video-analytics")
		print "Comp revision for " + comp + " is " + path_rev_dict[path] + "\n"
		#print "The list of paths of the components in this build are " + str(dummy_list) + "\n"
		#print "The number of components in the path list ending with /generic is " +  str(len(dummy_list)) + "\n"
	else:
		print "Error: parsing component gerrit revision ids for this build\n"

if __name__ == "__main__":
	main()
