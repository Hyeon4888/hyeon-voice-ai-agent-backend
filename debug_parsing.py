from app.models.table.realtime_agent import RealtimeAgent
from app.models.table.custom_agent import CustomAgent
from pydantic import parse_obj_as
from typing import Union

data = {
    "name": "test",
    "type": "realtime",
    "config": {
        "model": "gpt-4",
        "voice": "alloy"
    }
}

print(f"Input data: {data}")

try:
    # Try parsing directly
    agent = parse_obj_as(Union[RealtimeAgent, CustomAgent], data)
    print(f"Parsed as: {type(agent)}")
    print(f"Model: {getattr(agent, 'model', 'MISSING')}")
    print(f"Voice: {getattr(agent, 'voice', 'MISSING')}")
except Exception as e:
    print(f"Error parsing: {e}")

data_flat = {
    "name": "test",
    "model": "gpt-4",
    "voice": "alloy"
}
print(f"\nInput data (flat): {data_flat}")
try:
    agent = parse_obj_as(Union[RealtimeAgent, CustomAgent], data_flat)
    print(f"Parsed as: {type(agent)}")
    print(f"Model: {getattr(agent, 'model', 'MISSING')}")
except Exception as e:
    print(f"Error parsing flat: {e}")
