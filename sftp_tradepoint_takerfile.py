import os
import sys
import gzip
import shutil
import configparser
import paramiko
import psycopg2
from datetime import date, timedelta
from psycopg2 import sql
import logging

config = configparser.ConfigParser()
config.read('/usr/app/fxda/birt_report/cfg/tradepoint.properties')

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s : [%(name)s] - %(message)s',
        filename = config['default']['logfile'],
        filemode='a'
)
logger = logging.getLogger('SFTP_Load_TP_TakerFile')

# Set filename to today which will be Sunday when scheduled and the file is also ready on TradePoint side.
today_date = date.today()
f = 'All_Fields_' + str(today_date) + '.csv'
#### Edit the below to alter the date of the filename if TradePoint change the name of the file.
#td = timedelta(1) # Option to run on another day by setting timedelta above(td)
#start_date = today_date - td
#f = 'All_Fields_' + str(start_date) + '.csv'  # Option to run on another day by setting timedelta above(td)

def download_file(remote_server, ssh_user, ssh_key, taker_file, local_filepath, remote_export_filepath, remote_processed_filepath, port_number=22):

        c = None
        sftp = None
        try:
                ## Create transport instance and setup SFTP connection
                privatekeyfile = os.path.expanduser(ssh_key)
                mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname = remote_server,username = ssh_user, port = int(port_number), pkey = mykey)
                sftp = client.open_sftp()

                try:
                        ## Download New Takerfile to temporary /var/tmp/<<Takerfie>> from Tradepoint server ftp/export folder.
                        sftp.get(remote_export_filepath + taker_file , local_filepath + taker_file)

                        # Compress downlaoded CSV file
                        logger.info('Compressing CSV file for archiving')
                        with open('/var/tmp/' + taker_file , 'rb') as f_in:
                                with gzip.open('/var/tmp/' + taker_file + '.gz' , 'wb' ) as f_out:
                                        shutil.copyfileobj(f_in, f_out)
                        ## Move compressed Takerfile to ftp/processed on TradePoint remote server.
                        logger.info('Move compressed CSV file to /processed on TradePoint server.')
                        sftp.put(local_filepath + taker_file + '.gz' , remote_processed_filepath + taker_file + '.gz')
                        ## Remove Takerfile from export folder after processing
                        sftp.remove(remote_export_filepath + taker_file)

                except Exception as e:
                        print(f'Failed to transfer files: {e}')
                        logger.error(e)
                        exit(1)
        except Exception as e:
                ## print(f'Failed to transfer files: {e}')
                logger.error(e)
        finally:
                if sftp:
                        sftp.close()
                if client:
                        client.close()

def upload_file(remote_server, ssh_user, ssh_key, taker_file, local_filepath, remote_filepath, port_number=22):
        transport = None
        sftp = None
        try:
                ## Create transport instance and setup SFTP connection
                privatekeyfile = os.path.expanduser(ssh_key)
                mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                transport = paramiko.Transport((remote_server,int(port_number)))
                transport.connect(None, ssh_user,  pkey = mykey )
                sftp = paramiko.SFTPClient.from_transport(transport)
                try:
                        ## Upload New Takerfile from /var/tmp/<<Takerfie>> to S:\Matrix  folder.
                        sftp.put(local_filepath + taker_file + '.gz' , remote_filepath + taker_file  + '.gz')

                except Exception as e:
                        print(f'Failed to transfer file: {e}')
                        logger.error(e)
                        exit(1)
        except Exception as e:
                ## print(f'Failed to connect to remote sevrer and transfer file: {e}')
                logger.error(e)
        finally:
                if sftp:
                        sftp.close()
                if transport:
                        transport.close()

def fxda_db_load(local_filepath,taker_file):
        #Load configuration from file
        host = config['prod.database']['db_host']
        port = config['prod.database']['db_port']
        database = config['prod.database']['db_database']
        user = config['prod.database']['db_user']
        efx_table = config['prod.database']['db_table']

        conn = None

        #efx_table = 'efx_history.tradepoint_orders_test'
        csv_file = open(local_filepath + taker_file, "r")
        # Select query to upload TradePoint taker file to FXDA Postgres DB efx_history.tradepoint_orders"
        sql = "COPY %s FROM STDIN WITH DELIMITER AS ',' NULL 'NULL' CSV HEADER"
        try:
                #conn = psycopg2.connect(**db_params)
                conn = psycopg2.connect(dbname=database,user=user,host=host,port=port)
                cur = conn.cursor()
                cur.copy_expert(sql=sql % efx_table,file=csv_file)
                conn.commit()
                cur.close()
                logger.info(sql % efx_table)

        except (Exception, psycopg2.DatabaseError) as e:
                logger.error(e)
                print(e)
                sys.exit("Either DB SQL failed or could not connect to FXDA Postgres database.")
        finally:
                if conn is not None:
                        conn.close()

def tradepoint_download():
        #Load configuration from file
        u = config['prod.tradepoint']['ssh_user']
        h = config['prod.tradepoint']['host_1']
        k = config['prod.tradepoint']['privatekeyfile']
        ep = config['prod.tradepoint']['remote_export_filepath']
        pp = config['prod.tradepoint']['remote_processed_filepath']
        lp = config['default']['local_filepath']

        # Variable f comes from global variable for default filename
        download_file(h, u, k, f, lp, ep, pp)

def zkb_upload():
        #Load configuration from file
        u = config['prod.zkb']['ssh_user']
        h = config['prod.zkb']['host_1']
        k = config['prod.zkb']['privatekeyfile']
        fp = config['prod.zkb']['remote_filepath']
        lp = config['default']['local_filepath']

        # Variable f comes from global variable for default filename
        upload_file(h, u, k, f, lp, fp)

def main():
        logger.info('[Started]\t - Main')
        logger.info('Started]\t - Download of latest TradePoint Taker CSV file.')
        try:
                tradepoint_download()
        except Exception as e:
                logger.error('Problem with downloading Takerfile from TradePoint server. Existing script.')
                exit(1)
        logger.info('[Finished]\t - Downloading latest TradePoint Taker CSV file.')

        logger.info('Started]\t - Upload of latest TradePoint Taker CSV file to S:\Matrix.')
        try:
                zkb_upload()
        except Exception as e:
                logger.error('Problem with uploading Takerfile to S:\Matrix. Existing script.')
                exit(1)
        logger.info('[Finished]\t - Upload latest TradePoint Taker CSV file  to S:\Matrix.')

        logger.info('[Started]\t - Load of TradePoint Taker CSV file into FXDA database.')
        lp = config['default']['local_filepath']
        fxda_db_load(lp,f)
        logger.info('[Finished]\t - Load of TradePoint Taker CSV file into FXDA database.')
        logger.info('[Finished]\t - Main')

        ## Cleanup temporary Takerfile
        os.remove('/var/tmp/' + f) # f = taker file global variable

if __name__ == '__main__':
        main()
