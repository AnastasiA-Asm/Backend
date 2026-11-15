from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from moderation_router import router

app = FastAPI()
app.include_router(router)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in issue["loc"]),
            "message": issue["msg"],
        }
        for issue in error.errors()
    ]
    return JSONResponse(status_code=400, content={"detail": details})

@app.get("/")
async def root():
    return {"message": "Hello World"}