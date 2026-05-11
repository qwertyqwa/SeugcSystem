from rest_framework.views import exception_handler


def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data
    message = "Request failed."
    errors = data

    if isinstance(data, dict):
        if "detail" in data:
            message = str(data["detail"])
        elif "non_field_errors" in data and data["non_field_errors"]:
            message = str(data["non_field_errors"][0])
    elif isinstance(data, list) and data:
        message = str(data[0])

    response.data = {
        "success": False,
        "error": {
            "message": message,
            "details": errors,
        },
    }
    return response
