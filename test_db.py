import asyncio
from dotenv import load_dotenv
load_dotenv()
from src.config.db import db

async def test_db():
    print('Testing DB...')
    try:
        response = db.table('items').select('*').execute()
        print('SUCCESS:', response.data)
    except Exception as e:
        print(f'BUY PAGE ERROR: {e}')

if __name__ == "__main__":
    asyncio.run(test_db())
