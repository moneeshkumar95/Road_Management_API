import time
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host
        request_line = f"{request.method} {request.url.path}"

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            process_time = time.time() - start_time
            
            logger.exception(
                "Internal Server Error",
                extra={
                    "client_ip": client_ip,
                    "request_line": request_line,
                    "status_code": 500,
                    "process_time": process_time,
                }
            )
            print(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )

        process_time = time.time() - start_time
        logger.info(
            "",
            extra={
                "client_ip": client_ip,
                "request_line": request_line,
                "status_code": status_code,
                "process_time": process_time,
            }
        )
        return response