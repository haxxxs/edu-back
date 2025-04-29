from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "calendar_notes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "date" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "color" VARCHAR(20),
    "is_important" BOOL NOT NULL DEFAULT False
);
COMMENT ON TABLE "calendar_notes" IS 'Calendar note model for educational platform';
CREATE TABLE IF NOT EXISTS "courses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "level" VARCHAR(50) NOT NULL,
    "duration" VARCHAR(50) NOT NULL,
    "image_url" VARCHAR(512),
    "full_description" TEXT,
    "cover_image" VARCHAR(500),
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "courses" IS 'Database model for Educational Courses.';
CREATE TABLE IF NOT EXISTS "course_modules" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "lessons_count" INT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "course_id" INT NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "course_modules"."lessons_count" IS 'Number of lessons in the module';
COMMENT ON COLUMN "course_modules"."course_id" IS 'The course this module belongs to';
COMMENT ON TABLE "course_modules" IS 'Database model for Modules within an Educational Course.';
CREATE TABLE IF NOT EXISTS "events" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "start_date" TIMESTAMPTZ NOT NULL,
    "end_date" TIMESTAMPTZ NOT NULL,
    "location" VARCHAR(300),
    "max_participants" INT,
    "current_participants" INT NOT NULL DEFAULT 0,
    "type" VARCHAR(10) NOT NULL DEFAULT 'conference',
    "price" DECIMAL(10,2),
    "image_url" VARCHAR(500),
    "is_online" BOOL NOT NULL DEFAULT False
);
COMMENT ON COLUMN "events"."type" IS 'CONFERENCE: conference\nWORKSHOP: workshop\nWEBINAR: webinar\nMEETUP: meetup';
COMMENT ON TABLE "events" IS 'Event model for educational events';
CREATE TABLE IF NOT EXISTS "tasks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "status" VARCHAR(11) NOT NULL DEFAULT 'todo',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "due_date" TIMESTAMPTZ
);
COMMENT ON COLUMN "tasks"."status" IS 'TODO: todo\nIN_PROGRESS: in_progress\nCOMPLETED: completed\nCANCELLED: cancelled';
COMMENT ON TABLE "tasks" IS 'Task model for the educational platform';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "name" VARCHAR(100),
    "role" VARCHAR(7) NOT NULL DEFAULT 'student',
    "avatar_url" VARCHAR(512),
    "about" TEXT,
    "location" VARCHAR(100),
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_admin" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users"."role" IS 'STUDENT: student\nTEACHER: teacher\nADMIN: admin';
COMMENT ON TABLE "users" IS 'User model for the educational platform';
CREATE TABLE IF NOT EXISTS "user_courses" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "progress" INT NOT NULL DEFAULT 0,
    "status" VARCHAR(11) NOT NULL DEFAULT 'in_progress',
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_accessed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,
    "certificate_id" VARCHAR(100),
    "course_id" INT NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_course_user_id_80bce0" UNIQUE ("user_id", "course_id")
);
COMMENT ON COLUMN "user_courses"."status" IS 'COMPLETED: completed\nIN_PROGRESS: in_progress';
COMMENT ON TABLE "user_courses" IS 'Связь между пользователем и курсом, отслеживание прогресса';
CREATE TABLE IF NOT EXISTS "certificates" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "issued_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "certificate_url" VARCHAR(500),
    "user_course_id" INT NOT NULL UNIQUE REFERENCES "user_courses" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "certificates" IS 'Сертификат о прохождении курса';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
