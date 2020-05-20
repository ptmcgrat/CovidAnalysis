


def convertAgeGroupToTuple(age_group):
	if 'Under' in age_group:
		min_age = 0
		max_age = int(age_group.split(' ')[1]) - 1
	elif 'over' in age_group:
		min_age = int(age_group.split(' ')[0])
		max_age = 100
	elif 'to' in age_group:
		min_age = int(age_group.split(' ')[0])
		max_age = int(age_group.split(' ')[2])
	elif '-' in age_group:
		min_age = int(age_group.split('-')[0])
		max_age = int(age_group.split('-')[1].replace(' years',''))
	elif '+' in age_group:
		min_age = int(age_group.split('+')[0])
		max_age = 100
	return min_age,max_age