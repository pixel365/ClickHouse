import json
from datetime import datetime
from xml.etree import ElementTree as ET

import pytest

from helpers.cluster import ClickHouseCluster

cluster = ClickHouseCluster(__file__)
node_all_keys = cluster.add_instance(
    "node_all_keys", main_configs=["configs/config_all_keys_json.xml"]
)
node_some_keys = cluster.add_instance(
    "node_some_keys", main_configs=["configs/config_some_keys_json.xml"]
)
node_no_keys = cluster.add_instance(
    "node_no_keys", main_configs=["configs/config_no_keys_json.xml"]
)


@pytest.fixture(scope="module")
def start_cluster():
    try:
        cluster.start()
        yield cluster
    finally:
        cluster.shutdown()


def is_json(log_json):
    try:
        json.loads(log_json)
    except ValueError as e:
        return False
    return True


def validate_log_level(config, logs):
    root = ET.fromstring(config)
    key = root.findtext(".//names/level") or "level"

    valid_level_values = {
        "Fatal",
        "Critical",
        "Error",
        "Warning",
        "Notice",
        "Information",
        "Debug",
        "Trace",
        "Test",
    }

    length = min(10, len(logs))
    for i in range(0, length):
        json_log = json.loads(logs[i])
        if json_log[key] not in valid_level_values:
            return False
    return True


def is_valid_utc_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except ValueError:
        try:
            datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False


def validate_log_config_relation(config, logs, config_type):
    root = ET.fromstring(config)
    keys_in_config = set()

    if config_type == "config_no_keys":
        keys_in_config.add("date_time")
        keys_in_config.add("date_time_utc")
        keys_in_config.add("thread_name")
        keys_in_config.add("thread_id")
        keys_in_config.add("level")
        keys_in_config.add("query_id")
        keys_in_config.add("logger_name")
        keys_in_config.add("message")
        keys_in_config.add("source_file")
        keys_in_config.add("source_line")
    else:
        for child in root.findall(".//names/*"):
            keys_in_config.add(child.text)

    try:
        length = min(10, len(logs))
        for i in range(0, length):
            json_log = json.loads(logs[i])
            keys_in_log = set(json_log.keys())

            if not keys_in_config.issubset(keys_in_log):
                return False

            # Validate the UTC datetime format in "date_time_utc" if it exists
            if "date_time_utc" in json_log and not is_valid_utc_datetime(
                json_log["date_time_utc"]
            ):
                return False

    except ValueError as e:
        return False
    return True


def validate_logs(logs):
    length = min(10, len(logs))
    result = True
    for i in range(0, length):
        result = result and is_json(logs[i])
    return result


def validate_everything(config, node, config_type):
    node.query("SELECT 1")
    logs = node.grep_in_log("").split("\n")
    return (
        validate_logs(logs)
        and validate_log_config_relation(config, logs, config_type)
        and validate_log_level(config, logs)
    )


def test_structured_logging_json_format(start_cluster):
    config_all_keys = node_all_keys.exec_in_container(
        ["cat", "/etc/clickhouse-server/config.d/config_all_keys_json.xml"]
    )
    config_some_keys = node_some_keys.exec_in_container(
        ["cat", "/etc/clickhouse-server/config.d/config_some_keys_json.xml"]
    )
    config_no_keys = node_no_keys.exec_in_container(
        ["cat", "/etc/clickhouse-server/config.d/config_no_keys_json.xml"]
    )

    assert (
        validate_everything(config_all_keys, node_all_keys, "config_all_keys") == True
    )
    assert (
        validate_everything(config_some_keys, node_some_keys, "config_some_keys")
        == True
    )
    assert validate_everything(config_no_keys, node_no_keys, "config_no_keys") == True
