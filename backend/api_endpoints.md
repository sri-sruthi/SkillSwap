| Endpoint                     | Method | Request Body / Params                                                                           | Description                                     |
| ---------------------------- | ------ | ----------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `/init_db`                   | POST   | None                                                                                            | Initializes the SQLite database                 |
| `/add_user`                  | POST   | `{ "name": "Alice", "skills_known": ["Python"], "skills_want": ["Java"], "location": "Delhi" }` | Adds a new user                                 |
| `/get_matches?user_id=<id>`  | GET    | Query param                                                                                     | Returns best matches for a user based on skills |
| `/add_session`               | POST   | `{ "user_id":1, "teacher_id":2, "skill":"Python", "session_notes":"Practiced OOP basics" }`     | Logs a learning session                         |
| `/get_progress?user_id=<id>` | GET    | Query param                                                                                     | Returns all sessions for a user                 |
