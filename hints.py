# the function converts single word string to iterable list, so it can be used in for loop, list can be nested if needed
def get_iterable(x):
    if isinstance(x, collections.Iterable) and not isinstance(x, str):
        return x
    else:
        return ((x,),)

# kind of lame join for two lists of dictionaries (returned by pymysql.cursors.DictCursor) and build new dict
applications={}
for app_dict in app_dict_list:
    for adm_dict in adm_dictlist:
        if (app_dict['client_sponsor_id'] == adm_dict['client_sponsor_id']):
            applications[adm_dict['db_schema']]=app_dict['db_schema']


# create nested dictionary in recursion
def add_nested_key(nest, p_key, key):
    for k in nest:
        if k == p_key:
            nest[k][key] = {}
        else:
            add_nested_key(nest[k], p_key, key)
    return nest

# create parallel processes in AWS Lambda
from multiprocessing import Process, Pipe
def lambda_handler(event, context):
    '''
    I've been using it to run a code 4 times per minute,
    since lambda is triggered by cloudwatch rule once in a minute (with respect to cron schedule)
    4 processes is launched, each with sleep(sleep_time*i) delay 
    '''
    # number of subprocesses
    counter = int(os.environ['counter'])
    # delay
    sleep_time = int(60/counter)
    # create a list to keep all processes
    processes = []

    # create a list to keep connections
    parent_connections = []
    
    # create a process per instance
    for i in range(counter):
        # create a pipe for communication
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)

        # create the process, pass instance and connection
        process = Process(target=real_function, args=(i, sleep_time,event,))
        processes.append(process)

    # start all processes
    for process in processes:
        process.start()

    # make sure that all processes have finished
    for process in processes:
        process.join()
