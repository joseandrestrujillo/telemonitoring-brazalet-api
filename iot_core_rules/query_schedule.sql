SELECT end_device_ids.device_id, timestamp() as timestamp FROM 'lorawan/70B3D57ED005C19E/uplink' WHERE uplink_message.decoded_payload.is_query = 'true'