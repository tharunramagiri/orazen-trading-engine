#!/bin/bash

echo "Running Unit tests"

pytest --random-order --cov=orazen --cov-config=.coveragerc tests/
