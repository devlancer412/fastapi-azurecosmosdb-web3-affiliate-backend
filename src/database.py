import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import os
from config import cfg

HOST = cfg.ACCOUNT_HOST
MASTER_KEY = cfg.ACCOUNT_KEY
DATABASE_ID = cfg.COSMOS_DATABASE


class Database:
    def __init__(self) -> None:
        client = cosmos_client.CosmosClient(HOST, MASTER_KEY)

        self.db = client.create_database_if_not_exists(id=DATABASE_ID)
        print("Database with id '{0}' created".format(DATABASE_ID))

    def getContrainer(self, container_id, partition_key=None):
        if partition_key == None:
            return self.db.create_container_if_not_exists(
                id=container_id, partition_key=PartitionKey(path="/id", kind="Hash")
            )

        return self.db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path="/{}".format(partition_key), kind="Hash"),
        )


async def scale_container(container, size):
    print("\nScaling Container\n")

    # You can scale the throughput (RU/s) of your container up and down to meet the needs of the workload. Learn more: https://aka.ms/cosmos-request-units
    try:
        offer = container.read_offer()
        print("Found Offer and its throughput is '{0}'".format(offer.offer_throughput))

        offer.offer_throughput += size
        container.replace_throughput(offer.offer_throughput)

        print(
            "Replaced Offer. Offer Throughput is now '{0}'".format(
                offer.offer_throughput
            )
        )

    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 400:
            print("Cannot read container throuthput.")
            print(e.http_error_message)
        else:
            raise
