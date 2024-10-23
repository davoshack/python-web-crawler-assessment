import aiosqlite

async def store_response_data(url: str, status_code: int, content_size: int, page_title: str):
    async with aiosqlite.connect('db/crawler_data.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                url TEXT PRIMARY KEY,
            status_code INTEGER,
            content_size INTEGER,
            page_title TEXT
            )
        ''')
        await db.execute('''
            INSERT OR REPLACE INTO responses (url, status_code, content_size, page_title)
            VALUES (?, ?, ?, ?)
        ''', (url, status_code, content_size, page_title))
        await db.commit()
        await db.close()