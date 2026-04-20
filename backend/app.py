import os
import uvicorn
from config import prop

if __name__ == "__main__":
    uvicorn.run(
        "app.web.api:app",
        host=os.environ.get(prop['server']['host']),
        port=int(os.environ.get(prop['server']['port'])),
        reload=os.environ.get(prop['server']['reload']).lower() == 'true',
    )
