import asyncio
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as CP
from charger_manager.handlers import OcppHandlers

connected_chargers = {}  # charger_id: ChargePoint instance

class ChargePoint(CP):
    def __init__(self, id, websocket):
        super().__init__(id, websocket)
        self.handlers = OcppHandlers(self)

    @on("BootNotification")
    async def on_boot_notification(self, charge_point_model, **kwargs):
        return await self.handlers.handle_boot_notification(charge_point_model)

    @on("Heartbeat")
    async def on_heartbeat(self):
        return await self.handlers.handle_heartbeat()

    @on("Authorize")
    async def on_authorize(self, id_tag):
        return await self.handlers.handle_authorize(id_tag)

    @on("StartTransaction")
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        return await self.handlers.handle_start_transaction(
            connector_id, id_tag, meter_start, timestamp, **kwargs
        )

    @on("StopTransaction")
    async def on_stop_transaction(self, transaction_id, meter_stop, timestamp, **kwargs):
        return await self.handlers.handle_stop_transaction(
            transaction_id, meter_stop, timestamp, **kwargs
        )

async def on_connect(websocket, path):
    charger_id = path.strip("/")
    cp = ChargePoint(charger_id, websocket)
    connected_chargers[charger_id] = cp
    try:
        await cp.start()
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Charger {cp.id} disconnected.")
    except Exception as e:
        print(f"Unexpected error for charger {cp.id}: {e}")

async def start_websocket_server():
    server = await websockets.serve(on_connect, "0.0.0.0", 9000)
    print("WebSocket server started on port 9000...")
    await server.wait_closed()
