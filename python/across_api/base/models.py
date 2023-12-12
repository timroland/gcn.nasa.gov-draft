from dataclasses import dataclass
from typing import Any

from boto3.dynamodb.conditions import Key  # type: ignore

from ..api_db import dydbtable


class DynamoDBBase:
    __tablename__: str

    def save(self):
        table = dydbtable(self.__tablename__)
        table.put_item(Item=self.model_dump())

    @classmethod
    def get_by_key(cls, value: str, key: str):
        table = dydbtable(cls.__tablename__)
        response = table.query(KeyConditionExpression=Key(key).eq(value))
        items = response["Items"]
        if items:
            item = items[0]
            return cls(**item)
        return None

    @classmethod
    def delete_entry(cls, value: Any, key: str) -> bool:
        table = dydbtable(cls.__tablename__)
        return table.delete_item(Key={key: value})


@dataclass
class TLEEntryModelBase(DynamoDBBase):
    """Base for TLEEntry"""

    __tablename__ = ""
    epoch: str
    tle1: str
    tle2: str

    @classmethod
    def find_keys_between_epochs(cls, start_epoch, end_epoch):
        table = dydbtable(cls.__tablename__)
        # FIXME: Replace scan with a query here?
        response = table.scan(
            FilterExpression=Key("epoch").between(str(start_epoch), str(end_epoch))
        )
        items = response["Items"]
        tles = [cls(**item) for item in items]
        tles.sort(key=lambda x: x.epoch)
        return tles
