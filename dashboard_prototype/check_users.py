import asyncio
from app.database import async_session
from app.models import User
from app.auth.dependencies import verify_password
from sqlalchemy import select

async def check():
    async with async_session() as s:
        res = await s.execute(select(User))
        users = res.scalars().all()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"User: {u.username}, Role: {u.role}")
            if u.username == 'admin':
                print(f"  Password 'admin' verification: {verify_password('admin', u.password_hash)}")

if __name__ == '__main__':
    asyncio.run(check())
