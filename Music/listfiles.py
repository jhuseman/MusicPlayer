
import os

def listfiles(dir):
	paths = []
	for (subdir,subname,files) in os.walk(dir):
		for filename in files:
			paths.append(os.path.join(subdir,filename))
	return paths

def limit_ext(files,extensions):
	found = []
	for file in files:
		(not_ext,ext) = os.path.splitext(file)
		for comp_ext in extensions:
			if ext==comp_ext:
				found.append(file)
	return found
