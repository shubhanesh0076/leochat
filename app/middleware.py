from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from utils.helpers import get_payload
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi import status

origins = ["*"]


def apply_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):

        try:
            return JSONResponse(
                status_code=exc.status_code,
                content=get_payload(
                    message=str(exc.detail["message"]),
                    details=exc.detail["details"],
                    is_authenticated=exc.detail["is_authenticated"],
                    ok=exc.detail["ok"],
                ),
            )
        except Exception as e:
            print("ERROR: ", e)
            # print("New Error Occurse: ", e.__class__.__class__)
            return JSONResponse(
                status_code=exc.status_code,
                content=get_payload(
                    message="Token not provided.",
                    is_authenticated=False,
                    ok=False,
                ),
            )

    # Custom handler for RequestValidationError
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # Extract all errors
        errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
        error_message = errors[0].get("msg", None) if errors else errors

        # Get the first error type to determine the status code
        error_type = exc.errors()[0]["type"]

        # Determine the status code based on error type
        status_code = status.HTTP_403_FORBIDDEN
        if error_type == "missing":
            status_code = (
                status.HTTP_422_UNPROCESSABLE_ENTITY
            )  # You might need this condition for specific errors
            error_message = (
                f"{errors[0].get('loc')}, {errors[0].get('msg')}" if errors else errors
            )
        # Return the JSON response
        return JSONResponse(
            status_code=status_code,
            content=get_payload(
                message=error_message, is_authenticated=False, ok=False
            ),
        )

    return app
