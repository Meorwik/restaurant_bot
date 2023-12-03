import json


class JsonTool:
    @classmethod
    def serialize(cls, obj) -> str:
        """
        Method serializes python object into JSON serializable str object
        :return: JSON serializable str object
        """
        if isinstance(obj, dict):
            return json.dumps(obj, indent=4)
        elif isinstance(obj, str):
            return json.dumps(json.loads(obj))
        else:
            return json.dumps(obj, default=lambda o: o.__dict__, indent=4)

    @classmethod
    def deserialize(cls, json_data: str, object_class=None):
        """
        Method deserializes 'json_data' object into python object
        :return: object
        """
        object_data: dict = json.loads(json_data)
        if object_class is not None:
            return object_class(config=object_data)
        else:
            return object_data
