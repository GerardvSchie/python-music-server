import logging

from mpserver.grpc import mmp_pb2


def ok_response(message: str = "") -> mmp_pb2.MMPResponse:
    logging.debug(f"OK result: {message}")
    response = mmp_pb2.MMPResponse()
    response.result = mmp_pb2.MMPResponse.OK
    if message:
        response.message = message
    return response


def error_response(message: str = "") -> mmp_pb2.MMPResponse:
    logging.warning(f"ERROR result: {message}")
    response = mmp_pb2.MMPResponse()
    response.result = mmp_pb2.MMPResponse.ERROR
    if message:
        response.error = message
    return response


def empty_response() -> mmp_pb2.MMPResponse:
    logging.debug("Empty response")
    return mmp_pb2.MMPResponse()
