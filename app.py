"""
Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
Application Entry Point & Service Runner
"""

import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("================================================================")
    print("   EXTREME HEATWAVE EARLY WARNING & THERMAL STRESS PLATFORM     ")
    print("   Bioclimatic Surveillance & Civic Decision Support System     ")
    print(f"   Server operational on: http://127.0.0.1:{port}               ")
    print("================================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
