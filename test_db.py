import asyncio
import db

async def main():
    try:
        await db.connect_db()
        r = await db.db.fetchrow("SELECT count(*) FROM books")
        print('books count:', r['count'] if r else r)
    except Exception as e:
        print('DB test failed:', e)
    finally:
        await db.close_db()

if __name__ == '__main__':
    asyncio.run(main())
