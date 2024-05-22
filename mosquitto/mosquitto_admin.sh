#!/bin/sh

create_or_delete_user() {
  message="$1"
  command=$(echo "$message" | jq -r '.command')
  username=$(echo "$message" | jq -r '.name')
  password=$(echo "$message" | jq -r '.password')
  
  if [ -n "$command" ]; then
    if [ "$command" = "create" ]; then
      if [ -n "$username" ] && [ -n "$password" ]; then
        echo "Creating user: $username"
        mosquitto_passwd -b /mosquitto/config/passwd "$username" "$password"
        kill -HUP $(pidof mosquitto)
      else
        echo "Invalid message format: $message"
      fi
    elif [ "$command" = "delete" ]; then
      if [ -n "$username" ]; then
        echo "Deleting user: $username"
        mosquitto_passwd -D /mosquitto/config/passwd "$username" 
        kill -HUP $(pidof mosquitto)
      else
        echo "Invalid message format: $message"
      fi
    else
      echo "Unknown command: $command"
    fi
  else
    echo "No command provided in message: $message"
  fi
}

mosquitto -c /mosquitto/config/mosquitto.conf &

mosquitto_sub -h localhost -p 1883 -u admin-broker -P AdmBro@1984 -t cloud/admin/user | while read -r message; do
  create_or_delete_user "$message"
done
