from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from astral import LocationInfo
from astral.sun import sun
from datetime import date
import pytz,uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

@app.get("/sunlight")
def get_sunlight(lat: float = Query(...), lng: float = Query(...), tz: str = Query("Asia/Taipei")):
    location = LocationInfo(latitude=lat, longitude=lng, timezone=tz)
    s = sun(location.observer, date=date.today(), tzinfo=pytz.timezone(tz))
    return {
        "sunrise": s["sunrise"].isoformat(),
        "sunset": s["sunset"].isoformat(),
        "now": s["noon"].isoformat()
    }

if __name__=="__main__":
    uvicorn.run("main:app",reload=True)