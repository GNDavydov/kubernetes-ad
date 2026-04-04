import time
from uuid import UUID


def detect(model_id: UUID, integration_id: UUID):
    print("Detecting.....")
    print(model_id)
    print(integration_id)
    time.sleep(10)
