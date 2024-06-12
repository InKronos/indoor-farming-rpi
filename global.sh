#!/bin/bash

# Uruchomienie connect.bash
./connect_to_wifi.sh

# Uruchomienie ble_server.py
./ble-env/bin/python3 ble_server.py &

# Funkcja sprawdzająca połączenie z Wi-Fi
check_wifi() {
  if iwgetid -r &> /dev/null; then
    echo "Wi-Fi is connected."
    return 0
  else
    echo "Wi-Fi is not connected."
    return 1
  fi
}

# Uruchomienie skryptów
start_scripts() {
  python3 Myzeroconf.py &
  MYZEROCONF_PID=$!
  python3 app.py &
  SERVER_PID=$!
  echo "Started Myzeroconf.py (PID: $MYZEROCONF_PID) and server.py (PID: $SERVER_PID)"
}

# Zatrzymanie skryptów
stop_scripts() {
  if [[ ! -z "$MYZEROCONF_PID" ]]; then
    kill $MYZEROCONF_PID
    echo "Stopped Myzeroconf.py (PID: $MYZEROCONF_PID)"
  fi
  if [[ ! -z "$SERVER_PID" ]]; then
    kill $SERVER_PID
    echo "Stopped server.py (PID: $SERVER_PID)"
  fi
}

# Pętla sprawdzająca połączenie z Wi-Fi co 10 sekund
while true; do
  if check_wifi; then
    if [[ -z "$MYZEROCONF_PID" || -z "$SERVER_PID" ]]; then
      start_scripts
    fi
  else
    stop_scripts
    MYZEROCONF_PID=""
    SERVER_PID=""
  fi
  sleep 10
done