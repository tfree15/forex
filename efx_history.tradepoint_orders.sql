--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7
-- Dumped by pg_dump version 11.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: tradepoint_orders; Type: TABLE; Schema: efx_history; Owner: postgres
--

CREATE TABLE efx_history.tradepoint_orders (
    algorithm text,
    hold_times double precision,
    clordid text,
    adapter text,
    sender text,
    symbol text,
    side text,
    avg_px double precision,
    cum_qty bigint,
    limit_px double precision,
    open_qty bigint,
    sending_time timestamp with time zone NOT NULL,
    account text,
    portfolio text,
    status text,
    orig_qty bigint,
    canceled_qty double precision,
    canceled_by text,
    venue_name text,
    venue_root_id text,
    algorithm2 text,
    inbound_root_id text,
    time_in_force text,
    is_open boolean,
    is_filled boolean,
    is_cancelled boolean,
    is_rejected boolean,
    parent_order_id text,
    accept_or_reject_reason text,
    order_source bigint,
    orig_sender text,
    order_id text,
    close_time timestamp with time zone,
    root_id text,
    risk_impact double precision,
    vwap_midpoint double precision,
    hedged_qty double precision,
    hedged_value double precision,
    hedged_time timestamp with time zone,
    hedge_attributable double precision,
    pnl double precision,
    owner double precision,
    baseowner double precision,
    expire_time timestamp with time zone,
    related_algo_id text,
    wave_id bigint,
    session_id bigint,
    oversent_qty double precision,
    prime_broker double precision,
    mkt_update_received_time bigint,
    mkt_update_processed_time bigint,
    mkt_update_enter_algo_time bigint,
    order_enter_venue_queue_time bigint,
    order_before_send_to_venue_time bigint,
    order_after_send_to_venue_time bigint,
    incoming_order_received_time bigint,
    incoming_order_enter_algo_time bigint,
    gui_send_time bigint,
    strategy double precision,
    strategy_params double precision,
    inbound_adapter_type text,
    quote_id text,
    currency text,
    best_opposing_price double precision,
    wcp_server_submit double precision,
    sumqty_server_submit double precision,
    market_data_age bigint,
    oe_dialog boolean,
    oe_dialog_open text,
    oe_dialog_submit text,
    wcp_dialog_submit double precision,
    sumqty_dialog_submit double precision,
    wcp_server_arrive double precision,
    sumqty_server_arrive double precision,
    oe_init_price double precision,
    oe_init_qty double precision,
    oe_init_price_source text,
    vwap_shows_wcp boolean,
    oe_initial_peg_side text,
    oe_init_wcp double precision,
    oe_init_sum_qty double precision,
    clock_drift_micros double precision,
    latency_micros double precision,
    best_agg_arrive double precision,
    best_primary_arrive double precision,
    included_feeds text,
    small_order_size double precision,
    home_ccy_rate double precision,
    client_fee double precision,
    risk_book text,
    order_close_event_time bigint,
    order_close_algo_time bigint,
    incoming_algo_start_time bigint,
    event_generated_time bigint,
    event_system_time bigint,
    event_algo_queue_time bigint,
    event_algo_processed_time bigint,
    event_reason bigint,
    normalised_venue_name text,
    is_full_amount boolean,
    spot_margin double precision,
    fwd_margin double precision
);


ALTER TABLE efx_history.tradepoint_orders OWNER TO postgres;

--
-- Name: tradepoint_orders_v3_sending_time_idx1; Type: INDEX; Schema: efx_history; Owner: postgres
--

CREATE INDEX tradepoint_orders_v3_sending_time_idx1 ON efx_history.tradepoint_orders USING btree (sending_time DESC);


--
-- Name: tradepoint_orders ts_insert_blocker; Type: TRIGGER; Schema: efx_history; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON efx_history.tradepoint_orders FOR EACH ROW EXECUTE PROCEDURE _timescaledb_internal.insert_blocker();


--
-- Name: TABLE tradepoint_orders; Type: ACL; Schema: efx_history; Owner: postgres
--

GRANT ALL ON TABLE efx_history.tradepoint_orders TO efx_analyst;
GRANT SELECT,INSERT,UPDATE ON TABLE efx_history.tradepoint_orders TO efx_ingest;
GRANT SELECT,INSERT,UPDATE ON TABLE efx_history.tradepoint_orders TO superset;


--
-- PostgreSQL database dump complete
--
