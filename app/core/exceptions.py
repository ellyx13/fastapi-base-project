from exceptions import CustomException

class ErrorCode:
    @staticmethod
    def NotFound(service_name: str, item: str):
        return CustomException(
            type=f"{service_name}/warning/not-found",
            status=404,
            title="Not Found.",
            detail=f"{service_name.capitalize()} with {item} could not be found."
        )

    @staticmethod
    def NotModified(service_name: str):
        return CustomException(
            type=f"{service_name}/warning/not-modified",
            status=304,
            title="Not Modified.",
            detail="Content has not changed since the last request. No update needed."
        )

    @staticmethod
    def Conflict(service_name: str, item: str):
        return CustomException(
            type=f"{service_name}/warning/conflict",
            status=409,
            title="Conflict.",
            detail=f"The {item} data already exists. Please provide other data and try again."
        )

