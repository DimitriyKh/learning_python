#!/usr/bin/python3

import os
import sys
import logging
import pymysql
import argparse
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='wrapper for sqitch')
try:
    parser.add_argument('--application',default='PM',type=str,help='application code to run the migration on. Defaults to PM')
    parser.add_argument('--ignore',nargs='+',default='',help='list of db_schema\'s to skip in migration')
    parser.add_argument('--db_server',type=str,required=True,help='endpoint to master DB server')
    parser.add_argument('--db_user',type=str,required=True,help='user to connect to db_server')
    parser.add_argument('--db_pass',type=str,required=True,help='password of db_user for db_server')
    parser.add_argument('--db_port',default=3306,type=int,help='port to connect on db_server. Default = 3306')
    parser.add_argument('--command',type=str,required=True,help='sqitch command to run: deploy/revert/verify/etc . command-options not supported (yet?)')
    parser.add_argument('--top_dir',type=str,help='dir where sqitch prjoject/sqitch.conf/sqitch.plan are located')

    args=parser.parse_args()

except Exception as ex:
    logger.error("ERROR: Unexpected error: Could not parse input parameters. %s", ex)
    sys.exit()


try:
    db_connect = pymysql.connect(args.db_server,args.db_user,args.db_pass)
except Exception as ex:
    logger.error("ERROR: Unexpected error: Could not connect to source MySQL instance. %s", ex)
    sys.exit()


# prepare a cursor object using cursor() method
s_cursor = db_connect.cursor()


#check if target db is platform, else get the list of app db's on server
if (args.application == 'PM'):
    applications =(('platform','platform'),)
else:
    sql="""SELECT adm.db_schema,app.db_schema FROM platform.configurations app
           LEFT JOIN platform.applications ON app.app_id = applications.id
           LEFT JOIN platform.configurations adm USING (client_sponsor_id)
           LEFT JOIN platform.applications adm_app ON adm.app_id = adm_app.id
           WHERE applications.code = %s AND adm_app.code = 'ADM';"""

    try:
        s_cursor.execute(sql,args.application)
        applications = s_cursor.fetchall()

        db_connect.close()

    except Exception as ex:
        logger.error("ERROR: Could not fetch data from source. %s", ex)
        db_connect.close()
        sys.exit()



for app in applications:
#app[1] is app.db_schema, app[0] is adm.db_schema
    if app[1] not in args.ignore:
        target_url="db:mysql://"+args.db_user+":"+args.db_pass+"@"+args.db_server+"/"+app[1]
        registry_db=app[0]+"_sqitch"
#add new target with name of app_schema
        add_target = subprocess.run(["sqitch","target","add",app[1],target_url,"--registry",registry_db],cwd=args.top_dir)
#run migration on the target
        run_sqitch = subprocess.run(["sqitch","--top-dir",args.top_dir]+args.command.split()+[ "-t",app[1]],cwd=args.top_dir)
