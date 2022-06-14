# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
from datetime import datetime

import mgp

API_URLS = {}
ORDER_NUMBER = 0


@mgp.read_proc
def create_push_stream(
    context: mgp.ProcCtx,
    stream_name: str,
    api_url: str,
) -> mgp.Record(created=bool):
    global API_URLS

    if not isinstance(stream_name, str):
        raise TypeError("Invalid type on first argument!")

    if not isinstance(api_url, str):
        raise TypeError("Invalid type on second argument!")

    API_URLS[stream_name] = api_url

    return mgp.Record(created=True)


@mgp.read_proc
def show_streams(
    context: mgp.ProcCtx,
) -> mgp.Record(name=str, api_url=str):
    records = []

    for k, v in API_URLS.items():
        records.append(mgp.Record(name=k, api_url=v))

    return records


@mgp.read_proc
def push(
    context: mgp.ProcCtx,
    stream_name: str,
    payload: mgp.Map,
) -> mgp.Record(status=str):

    if not isinstance(stream_name, str):
        raise TypeError("Invalid type on first argument!")

    if not isinstance(payload, dict):
        raise TypeError("Invalid type on second argument!")

    if stream_name not in API_URLS:
        raise Exception("Power BI stream not defined!")

    api_url = API_URLS[stream_name]

    message = ""
    if isinstance(payload, dict):
        message = payload
    elif isinstance(payload, mgp.Vertex) or isinstance(payload, mgp.Edge):
        message = {x.name: x.value for x in payload.properties.items()}
    else:
        raise Exception("Can't have message type other than Map / Vertex / Edge")

    for k, v in message.items():
        if isinstance(v, datetime):
            message[k] = datetime.strftime(v, "%Y-%m-%dT%H:%M:%S")

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.request(method="POST", url=api_url, headers=headers, data=json.dumps(message))
    except Exception as e:
        raise Exception(f"Error happened while sending results! {e}")

    return mgp.Record(status=str(response.status))
