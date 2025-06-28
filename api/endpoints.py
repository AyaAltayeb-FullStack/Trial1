from fastapi import APIRouter, HTTPException
from charger_manager.ws_server import connected_chargers

router = APIRouter()

# ✅ List all connected chargers
@router.get("/chargers")
def list_chargers():
    return {"connected_chargers": list(connected_chargers.keys())}

# ✅ Send RemoteStartTransaction
@router.post("/remote-start/{charger_id}")
async def remote_start(charger_id: str):
    cp = connected_chargers.get(charger_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Charger not connected")
    return await cp.handlers.send_remote_start_transaction()

# ✅ Send RemoteStopTransaction
@router.post("/remote-stop/{charger_id}")
async def remote_stop(charger_id: str):
    cp = connected_chargers.get(charger_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Charger not connected")

    tx_id = cp.handlers.active_transactions.get(cp.id)
    if not tx_id:
        raise HTTPException(status_code=400, detail="No active transaction found")

    return await cp.handlers.send_remote_stop_transaction(tx_id)

# ✅ Get transaction logs (in-memory)
@router.get("/logs/{charger_id}")
def get_logs(charger_id: str):
    cp = connected_chargers.get(charger_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Charger not found")
    return {"logs": cp.handlers.transaction_logs}
