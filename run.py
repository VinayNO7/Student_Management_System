#!/usr/bin/env python
"""
Student Management System Launch Script
Run this script to start the FastAPI server with frontend.
Usage:
    python run.py
"""

import sys
import uvicorn
from app.config import APP_HOST, APP_PORT, DEBUG, db_info

def print_banner():
    banner = f"""
========================================================================
           🎓 STUDENT MANAGEMENT SYSTEM (SMS) - DBMS 🎓
========================================================================
 * Backend Engine : Python FastAPI
 * Database Mode  : {db_info['engine'].upper()} ({'Connected' if db_info['connected'] else 'Disconnected'})
 * Target Database: {db_info['database']}
 * Server URL     : http://{APP_HOST}:{APP_PORT}
 * Swagger Docs   : http://{APP_HOST}:{APP_PORT}/docs
 * ReDoc          : http://{APP_HOST}:{APP_PORT}/redoc
========================================================================
 Status Note: {db_info['message']}
========================================================================
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    try:
        uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)
    except KeyboardInterrupt:
        print("\n[Shutdown] Server stopped by user.")
        sys.exit(0)

