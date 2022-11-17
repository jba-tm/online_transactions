#!/bin/bash

su - postgres -c "psql -t -c \"ALTER SYSTEM SET max_prepared_transactions = 100;\""
