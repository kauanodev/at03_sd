import asyncio
from amqtt.broker import Broker

config = {
    "listeners": {
        "deafault":{"type": "tcp","bind": "127.0.0.1:1883"}
    },
    "sys_interval": 0,
    "auth": {"allow-anonymous": True, "plugins": ["auth_anonymous"]},
    "topic-check": {"enabled": False},
    
}

async def main():
    broker = Broker(config)
    await broker.start()
    print("Broker MQTT rodando em localhost:1883(CTRL+C PARA PARAR)")
    await asyncio.Event().wait()

asyncio.run(main())
    