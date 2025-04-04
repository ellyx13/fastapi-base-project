from fastapi.responses import JSONResponse


class MiddlewareErrorCode:
    @staticmethod
    def SomeThingWentWrong():
        response = {}
        response["type"] = "middlewares/error/something-went-wrong"
        response["status"] = 500
        response["title"] = "Something went wrong."
        response["detail"] = "An unexpected error occurred. Please try again later."
        return JSONResponse(status_code=500, content=response)
