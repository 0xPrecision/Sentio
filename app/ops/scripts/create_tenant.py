import argparse, uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import insert
import asyncio
from app.infra.db import SessionLocal
from app.infra.models import Tenant

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--plan", default="starter")
    args = p.parse_args()

    async def _do():
        async with SessionLocal() as s:
            await s.execute(insert(Tenant).values(
                id=uuid.uuid4(),
                slug=args.slug,
                locale="ru",
                timezone="Europe/Minsk",
                plan=args.plan,
                plan_status="trial",
                trial_until=datetime.now(timezone.utc) + timedelta(days=14),
            ))
            await s.commit()
        print(f"Created tenant '{args.slug}'")

    asyncio.run(_do())

if __name__ == "__main__":
    main()
