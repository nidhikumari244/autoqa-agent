import sys
import asyncio
import uvicorn
from uvicorn.config import Config

config = Config("app.main:app", host="0.0.0.0", port=8000, reload=True, loop="none")
print("Reload:", config.should_reload)
print("use_subprocess:", config.use_subprocess)
factory = config.get_loop_factory()
print("Factory returned:", factory)

# In Python 3.11+, asyncio.Runner or asyncio.run with loop_factory=None:
runner = asyncio.Runner(loop_factory=factory)
loop = runner.get_loop()
print("Loop created by asyncio runner:", type(loop))
runner.close()
