from aioredis import Redis as AIORedis
from fastapi import FastAPI as BaseFastAPI


class FastAPI(BaseFastAPI):
    aioredis_instance: AIORedis

    async def configure(
            self,

            aioredis_instance: AIORedis,

    ):
        self.aioredis_instance = aioredis_instance
