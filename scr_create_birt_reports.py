import stats_calc_publish.DB.PostgresConnector as pg
import stats_calc_publish.DB.std_db_conn as db_conns
import stats_calc_publish.Tools.tzTools as tzTools
import stats_calc_publish.tradepoint_birt_reports.data.db_data as db_data
import stats_calc_publish.tradepoint_birt_reports.data.cfg_data as cfg_reader
import stats_calc_publish.tradepoint_birt_reports.calc.calc_reports as calc_rep
import logging
import pandas as pd
import sys
import argparse
import datetime


def valid_data(s):
    try:
        return pd.to_datetime(s, format="%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        msg = f"Not a valid date: {s}"
        raise argparse.ArgumentTypeError(msg)


def check_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from_date', type=valid_data, default='2021-07-01',
                        help='Date to start report from, use format yyyy-mm-dd')
    parser.add_argument('--to_date',  type=valid_data, default='2021-08-01',
                        help='Date to end report with, use format yyyy-mm-dd')
    parser.add_argument('--user', type=str, default='efx_analyst',
                        help='user to run script with, defaults to efx_analyst')
    parser.add_argument('--config', type=str, default='default',
                        help='Name of config profile to use')
    parser.add_argument('--env', type=str, default='eng', choices=['prod', 'st', 'eng'],
                        help='Environment to use, must be on of prod, st or eng, defaults to eng')
    c_args = parser.parse_args()
    if c_args.from_date is None:
        raise ValueError("ERROR: Argument from_date must be provided, aborting now")
    if c_args.to_date is None:
        raise ValueError("ERROR: Argument to_date must be provided, aborting now")
    return c_args

def get_runid():
    """
    Returns a valid run id
    """
    t = pd.Timestamp.now().to_datetime64().item(0)
    return int(t / 1e9)

def main(from_date: str, to_date: str, user: str, config_name: str, env: str) -> int:
    """
    Fetches data and calcs birt reports, writing the results to fxda
    from_date, to_date define the data range to be used, the time part will automatically be added to ensure full days
    user and env are the username (e.g. efx_analyst) and the environement(prod, eng, st) to be used
    config_name is the name of the config to be read from quant.birt_report_config, use 'default' if unsure
    Returns an int, to be used to identify the data written, or as an error indicator (if < 0)
    """
    cfg_table = 'quant.birt_report_config'

    # open connection
    try:
        db_cfg = db_conns.get_std_kerberos_conn(user=user, env=env, mode='rw')
        conn = pg.PostgresConnector(host=db_cfg['host'], port=db_cfg['port'], username=db_cfg['username'],
                                    database=db_cfg['database'], mode=db_cfg['mode'], log_level=logging.INFO)
    except Exception as err:
        print(f"ERROR: Could not open DB connection, error was {err}, aborting now")
        return -1

    # read config from db
    try:
        cfg = cfg_reader.fetch_birt_report_cfg(conn, cfg_table=cfg_table, cfg_name=config_name)
    except:
        cfg = None
    if cfg is None:
        conn.disconnect()
        print(f"ERROR: Config named {config_name} could not be read, aborting")
        return -1

    # check config
    for rb in cfg['risk_books']:
        if not rb in cfg['feeds_per_risk_book']:
            print(f"ERROR: Risk book {rb} is not configured in config column feeds_per_risk_book, aborting now")
            conn.disconnect()
            return -1

    # check date, add time part (ensuring full days), set time zone to Zurich
    from_date = tzTools.bod(tzTools.localize_ts(from_date, 'Europe/Zurich'))
    to_date = tzTools.eod(tzTools.localize_ts(to_date, 'Europe/Zurich'))

    # set epoch timestamp
    t_epoch = get_runid()

    # fetch data
    print(f"INFO: Fetching tradepoint data")
    df_data = db_data.get_lp_report_data(conn, from_date, to_date, cfg['trdpnt_orders_table'])
    if df_data is None or len(df_data) < 1:
        print(f"WARNING: No data could be fetched between {from_date} and {to_date}, aborting")
        conn.disconnect()
        return 0

    # for each metric, fetch data
    try:
        print(f"INFO: Calculating metrics")
        d_comp_metrics = calc_rep.calc_lp_reports(df_data, cfg['metrics'], cfg['risk_books'], cfg['feeds_per_risk_book'])
    except Exception as err:
        print(f"ERROR: Metrics calc failed, error was {err}, aborting now")
        conn.disconnect()
        return -1

    # write to db
    if d_comp_metrics is None:
        print("ERROR: No data to write, aborting now")
        conn.disconnect()
        return -1
    try:
        #db_data.write_lp_shares(conn, d_comp_metrics, cfg['risk_books'], t_epoch, args.from_date, args.to_date,cfg['output_table'], n_ccny=10, n_venues=15)
        db_data.write_lp_shares(conn, d_comp_metrics, cfg['risk_books'], t_epoch, from_date, to_date,cfg['output_table'], n_ccny=None, n_venues=None)
        db_data.write_std_metric(conn, d_comp_metrics, cfg['risk_books'], t_epoch, from_date, to_date, cfg['output_table'], 'holding_time')
        db_data.write_std_metric(conn, d_comp_metrics, cfg['risk_books'], t_epoch, from_date, to_date, cfg['output_table'], 'fill_ratio')
    except Exception as err:
        print(f"ERROR: Metrics writing failed, error was {err}, aborting now")
        return -1

    return t_epoch


if __name__ == '__main__':
    # get parameters
    # reactivate
    args = check_input()

    # activate for testing purposes
    # args.user='gb155'
    # args.env='prod'
    # args.from_date = '2021-09-27'
    # args.to_date = '2021-10-01'

    # info
    print(f"INFO: Script will run between "
          f"{args.from_date} and {args.to_date}, using config {args.config} in {args.env} for {args.user}")
    # run, return t_epoch or error flag
    res = main(from_date=args.from_date, to_date=args.to_date, user=args.user, config_name=args.config, env=args.env)
    print(f"INFO: Done, result is {res}")
    sys.exit(res)
