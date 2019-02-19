#!/bin/bash
celery -A app worker --loglevel=info
