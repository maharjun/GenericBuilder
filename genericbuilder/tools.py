__author__ = 'Arjun Rao'
def get_builder_type(obj_or_class):
	if 'builder_type' in dir(obj_or_class):
		builder_type = obj_or_class.builder_type
	else:
		builder_type = None
	return builder_type