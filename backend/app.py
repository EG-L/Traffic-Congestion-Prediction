import os
import uvicorn
from dotenv import load_dotenv
from config import prop

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.web.api:app",
        host=os.environ.get(prop['server']['host']),
        port=int(os.environ.get(prop['server']['port'])),
        reload=os.environ.get(prop['server']['reload']).lower() == 'true',
    )
