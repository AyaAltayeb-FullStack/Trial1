from ocpp.v16 import call_result, call
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus, RemoteStartStopStatus

class OcppHandlers:
    def __init__(self, cp):
        self.cp = cp
        self.active_transactions = {}  # Tracks active sessions per charger
        self.transaction_logs = []     # Stores simple transaction events

    # -------------------------------
    # ✅ BootNotification handler
    async def handle_boot_notification(self, charge_point_model):
        print(f"{self.cp.id} booted with model {charge_point_model}")
        return call_result.BootNotificationPayload(
            current_time=self.cp._now(),
            interval=10,
            status=RegistrationStatus.accepted
        )

    # -------------------------------
    # ✅ Heartbeat handler
    async def handle_heartbeat(self):
        print(f"{self.cp.id} sent Heartbeat")
        return call_result.HeartbeatPayload(current_time=self.cp._now())

    # -------------------------------
    # ✅ Authorize handler
    async def handle_authorize(self, id_tag):
        print(f"{self.cp.id} Authorize request for {id_tag}")
        return call_result.AuthorizePayload(
            id_tag_info={"status": AuthorizationStatus.accepted}
        )

    # -------------------------------
    # ✅ StartTransaction handler
    async def handle_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        print(f"{self.cp.id} StartTransaction from {id_tag}")

        transaction_id = 100001  # In real use, generate dynamically
        self.active_transactions[self.cp.id] = transaction_id

        self.transaction_logs.append({
            "event": "start",
            "charge_point": self.cp.id,
            "timestamp": timestamp,
            "idTag": id_tag,
            "transactionId": transaction_id
        })

        return call_result.StartTransactionPayload(
            transaction_id=transaction_id,
            id_tag_info={"status": AuthorizationStatus.accepted}
        )

    # -------------------------------
    # ✅ StopTransaction handler
    async def handle_stop_transaction(self, transaction_id, meter_stop, timestamp, **kwargs):
        print(f"{self.cp.id} StopTransaction")

        self.transaction_logs.append({
            "event": "stop",
            "charge_point": self.cp.id,
            "timestamp": timestamp,
            "transactionId": transaction_id,
            "meterStop": meter_stop
        })

        self.active_transactions.pop(self.cp.id, None)

        return call_result.StopTransactionPayload(
            id_tag_info={"status": AuthorizationStatus.accepted}
        )

    # -------------------------------
    # ✅ RemoteStartTransaction (server → charger)
    async def send_remote_start_transaction(self):
        print(f"Sending RemoteStartTransaction to {self.cp.id}")

        request = call.RemoteStartTransactionPayload(
            id_tag="valid123",
            connector_id=1
        )

        response = await self.cp.call(request)
        return {
            "action": "RemoteStartTransaction",
            "status": response.status.value
        }

    # -------------------------------
    # ✅ RemoteStopTransaction (server → charger)
    async def send_remote_stop_transaction(self, transaction_id):
        print(f"Sending RemoteStopTransaction to {self.cp.id}")

        request = call.RemoteStopTransactionPayload(transaction_id=transaction_id)
        response = await self.cp.call(request)

        return {
            "action": "RemoteStopTransaction",
            "status": response.status.value
        }
