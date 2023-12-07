#!/bin/bash

pytest -vvv  --cov=. --cov-report=html --no-cov-on-fail
