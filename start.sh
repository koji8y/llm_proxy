#!/bin/bash
uv run uvicorn server.server:app --host ${SERVER_ADDR:-127.0.0.1} --port ${SERVER_PORT:8000} $@
