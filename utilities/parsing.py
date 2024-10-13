from json_repair import repair_json


def stitch_response(raw_response: str) -> str:
    response = ''.join(raw_response)
    return response


def repair_json_response(raw_response: str) -> str:
    response  = repair_json(raw_response)
    return response
