#!/bin/bash

FILE="/tmp/wifi_credentials.txt"

# Create the file if it doesn't exist
if [ ! -f "$FILE" ]; then
    echo "" > "$FILE"
fi

# Function to connect to Wi-Fi
connect_to_wifi() {
    local wifi_name="$1"
    local wifi_password="$2"

    echo "Trying to connect to Wi-Fi: $wifi_name"
    # You need to adapt this part to your system's way of connecting to Wi-Fi
    # This is an example for systems using `nmcli`
    nmcli device wifi connect "$wifi_name" password "$wifi_password"
    if [ $? -eq 0 ]; then
        echo "Successfully connected to $wifi_name"
    else
        echo "Failed to connect to $wifi_name"
    fi
}

# Initial values
prev_wifi_name=""
prev_wifi_password=""

while true; do
    # Read the file
    content=$(cat "$FILE")
    # Extract Wi-Fi name and password
    wifi_name=$(echo "$content" | cut -d':' -f1)
    wifi_password=$(echo "$content" | cut -d':' -f2)
    
    # If the values have changed, try to connect
    if [[ "$wifi_name" != "$prev_wifi_name" || "$wifi_password" != "$prev_wifi_password" ]]; then
        prev_wifi_name="$wifi_name"
        prev_wifi_password="$wifi_password"
        if [[ -n "$wifi_name" && -n "$wifi_password" ]]; then
            connect_to_wifi "$wifi_name" "$wifi_password"
        fi
    fi

    # Sleep for a while before checking again
    sleep 10
done