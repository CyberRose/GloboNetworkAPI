#!/bin/bash

# NETAPI_ODL
echo "Waiting for ODL to go up"

MAX_RETRY=30
SLEEP_TIME=10

ODL_READY=0

for i in $(seq 1  ${MAX_RETRY}); do
    
    sleep ${SLEEP_TIME}
    docker exec ovs1 ovs-vsctl show | grep is_connected > /dev/null

    # If the port is open we continue with the script
    if [ "$?" -eq "0" ]; then
        break;
    fi
    
    # When maximum retries is achieved we exit with an error message
    if [ "$i" -eq "${MAX_RETRY}" ]; then
        echo "Max retry achieved"
        exit 1;
    fi

    echo "Retrying ${i}.."
done

echo "ODL server is ready";
