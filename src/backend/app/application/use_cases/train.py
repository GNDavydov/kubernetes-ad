import time
from uuid import UUID


def train(model_id: UUID, integration_id: UUID):
    print("Training.....")
    print(model_id)
    print(integration_id)
    time.sleep(10)
