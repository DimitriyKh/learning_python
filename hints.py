#the function converts single word string to iterable list, so it can be used in for loop, list can be nested if needed
def get_iterable(x):
    if isinstance(x, collections.Iterable) and not isinstance(x, str):
        return x
    else:
        return ((x,),)

#kind of lame join for two lists of dictionaries (returned by pymysql.cursors.DictCursor) and build new dict
applications={}
for app_dict in app_dict_list:
    for adm_dict in adm_dictlist:
        if (app_dict['client_sponsor_id'] == adm_dict['client_sponsor_id']):
            applications[adm_dict['db_schema']]=app_dict['db_schema']
