#/home/divyaven/bin/python

#import libraries

#global variables

#comp_dep_list_dict = {} #dictionary that stores (component,dependency_list) as key and value respectively
#for percentile calculation
#                        if not recZipYrDict.has_key(recipientId) :
#                                amtList = SortedList()
#                                amtList.add(float(fields[4]))
#                                recZipYrDict.update({recipientId:amtList})
#                        else :


def get_build_info(ip_file):
	line_marker_1 = False
	line_marker_2 = False
	line_cnt = 6
	with open(ip_file) as bldOutput:
		for line in bldOutput:
			if (line_marker_1 and line_marker_2):
				line_cnt = line_cnt - 1
				if (line_cnt <= 4 and line_cnt > 0):
					if (line_cnt == 4):
						print "Build info :\n"
						print "============\n"
					print line
			if (line_marker_1):
				if ("======================================" in line):
					line_marker_2 = True
			if ("INFO Build order:" in line):
				line_marker_1 = True

def build_dependency_graph(component, dep_list):
	if (component):
		if (dep_list):
			print "The dependency list for " + component + " is " + str(dep_list[-1]) + "\n" 
			#print "The length of the dependency list for " + component + " is " + str(len(dep_list)) + "\n" 
	return True

def parse_build_order(ip_file):
	parse_list_order = False
	ret = True #success
	with open(ip_file) as bldOutput:
		for line in bldOutput:
			if ("==============================================" in line):
                   		parse_list_order = False

               		if (parse_list_order and ret):
                   		parse_line = line.split(" ",5)
                   		if (len(parse_line) > 5):
                       			component_with_dep_list = parse_line[5]
					component = component_with_dep_list.split(" ")[0]
					tmp_dep_list = component_with_dep_list.split("[")[-1]
					dependency_list = tmp_dep_list.split("]")[0]
                       			#print component + "\n"
					#print dependency_list + "\n"
					dep_list = dependency_list.split(",")
					ret  = build_dependency_graph(component, dep_list)
               		else:
                   		if ("INFO Build order:" in line):
                       			parse_list_order = True
	return ret

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
	print "\n"
	print "The number of wanted lines from " + ip_file + " is " + str(num_lines) + "\n"
	return_value = parse_build_order(ip_file)
	if (return_value):
		print "Successfully built component dependency graph for this build\n"
	#get_build_info(ip_file)

if __name__ == "__main__":
	main()
