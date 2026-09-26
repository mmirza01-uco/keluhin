from domain.entities import user
from infrastructure.database import get_connection


class UserRepository:
    def find_by_id(self, user_id: str):
        connection = get_connection()

        try:
            row = connection.execute(
                """
                select * from users 
                    where id = ?
                """, (user_id),
            ).fetchone()

            if row is None:
                return None

            return self._to_entity(row)
        finally:
            connection.close()


    def find_by_email(self, email:str):
        connection = get_connection()

        try:

            row = connection.execute(
                """
                select * from users
                    where email = ?
                """,
                (email, ),
            ).fetchone()

            if row is None:
                return None

            return self._to_entity(row)

        finally:
            connection.close()


    def save(self, user: User):
        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                insert into users (
                    nama,
                    email,
                    password_hash,
                    peran,
                    dibuat_pada
                ) values (?,?,?,?,?)
                """,
                (user.User.nama,
                 user.User.email,
                 user.User.peran.value)
            )