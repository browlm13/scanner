#python 3

"""
		modual for handling confiugration files
			- read
			- add/delete
			- change
"""

#
#settings
#
COMMENT_CHAR = '#'

#
# pull value from config file
#

def get_value(config_fname, key):
	with open(config_fname, 'r') as f:
		default_settings = f.read()

	default_settings = default_settings.split('\n')
	for line in default_settings:
		if line[0] != COMMENT_CHAR:
			setting = line.split('=')
			if setting[0] == key:
				setting_value = setting[1]

	return setting_value

#
# set value in config file
#

def set_value(config_fname, key, value):

	#check if attribute exists
	with open(config_fname, 'r') as f:
		default_settings = f.read()

	default_settings = default_settings.split('\n')
	for i in range (0,len(default_settings)-1):
		if default_settings[0] != COMMENT_CHAR:
			setting = default_settings[i].split('=')
			if setting[0] == key:
				setting[1] = value
			default_settings[i] = setting[0] + "=" + setting[1]
	default_settings = '\n'.join(str(line) for line in default_settings)

	#write back to file
	with open(config_fname, 'w') as f:
		f.write(default_settings)
