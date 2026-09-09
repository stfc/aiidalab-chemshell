#!/bin/bash
# Start the AiiDA daemon before the default apps are installed (base image
# step 60). aiidalab 24.9.0 runs `verdi daemon restart` after pip-installing an
# app to load its plugin entry points, and treats a non-zero exit as fatal. The
# base image otherwise starts the daemon only at step 90, so without this the
# chemshell install fails at startup with "Critical: daemon is not running".
set -x
export SHELL=/bin/bash

# The profile (and RabbitMQ broker) are set up by the earlier boot scripts, so
# the daemon can start here. Tolerate failure so we never block container boot.
verdi daemon start || echo "ERROR: AiiDA daemon is not running!"
