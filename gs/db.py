import aiosqlite


async def add_to_db(telegram_id, user_group):
    async with aiosqlite.connect("gs/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, user_group TEXT)")
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ? AND user_group = ?",
                                  (telegram_id, user_group))
        data = await cursor.fetchone()
        if data is not None:
            return

        await db.execute("INSERT INTO users (telegram_id, user_group) VALUES(?, ?)", (telegram_id, user_group))
        await db.commit()


async def del_from_db(telegram_id, user_group):
    async with aiosqlite.connect("gs/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, user_group TEXT)")
        await db.execute("DELETE FROM users WHERE telegram_id = ? AND user_group = ?", (telegram_id, user_group))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect("gs/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, user_group TEXT)")
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()



# def main():
#     # Создаем event loop и запускаем корутину
#     users = asyncio.run(get_all_users())
#     print(users)
#
#
# if __name__ == "__main__":
#     main()
