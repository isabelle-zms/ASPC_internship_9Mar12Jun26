import meshtastic
import meshtastic.serial_interface
import copy

LOCALCONFIG_LORA_DEFAULT = {
    'use_preset': True,
    'modem_preset': 0,
    'bandwidth': 0,
    'spread_factor': 0,
    'coding_rate': 0,
    'frequency_offset': 0.0,
    'region': 'SG_923',
    'hop_limit': 3,
    'tx_enabled': True,
    'tx_power': 20,
    'channel_num': 0,
    'override_duty_cycle': False,
    'sx126x_rx_boosted_gain': False,   # PA to improve reception, but consumes more power
    'override_frequency': 0.0,
    'pa_fan_disabled': False,
    'ignore_incoming': [],
    'ignore_mqtt': True,               # Downlink: Ignore MQTT packets (which come via internet)
    'config_ok_to_mqtt': False,        # Uplink: OK to send my packet to server via MQTT?
}

localConfig_lora_working = copy.deepcopy(LOCALCONFIG_LORA_DEFAULT)


def config_lora(interface: meshtastic.serial_interface.SerialInterface, user_id: str, localConfig_lora_values: dict = LOCALCONFIG_LORA_DEFAULT) -> None:
    """
    Configures the lora field of a target node. Note: our node's public key must be included in target node's Admin Keys.

    Args:
        interface (meshtastic.serial_interface.SerialInterface): Our interface, which will be used to talk to the other node.
        user_id (str): The user ID of the target node. Hex representation of target node number, appended to '!', E.g. '!435a7004'
        localConfig_lora_values (dict): A dictionary of lora field values you want to configure.
  
    Returns:
        None
    """
    node = interface.getNode(user_id)
    node_lora_config = node.localConfig.lora
    valid_lora_fields = node_lora_config.DESCRIPTOR.fields_by_name.keys()

    node.beginSettingsTransaction()

    # Handle repeated field (a field type) 'ignore_incoming', which raises AttributeError when using setattr
    ignore_incoming_field = getattr(node_lora_config, 'ignore_incoming')
    ignore_incoming_field.clear()
    ignore_incoming_field.extend(localConfig_lora_values['ignore_incoming'])

    for key, value in localConfig_lora_values.items():
        # Handles outdated dictionary fields in the event of update
        if key not in valid_lora_fields:
            print(f"Warning: {key} is not a valid LoRa field")
            continue

        # Skip 'ignore_incoming' reapeted field type
        if key == 'ignore_incoming':
            continue
        
        # Update all remaining fields
        setattr(node_lora_config, key, value)

    node.writeConfig('lora')
    node.commitSettingsTransaction()
    print("Transaction succesful! Node will reboot in a short while.")