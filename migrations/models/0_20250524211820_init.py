from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "courses" (
    "id" UUID NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL UNIQUE,
    "description" VARCHAR(500) NOT NULL,
    "full_description" TEXT NOT NULL,
    "level" VARCHAR(12) NOT NULL,
    "duration" VARCHAR(50) NOT NULL,
    "image_url" VARCHAR(500),
    "cover_image" VARCHAR(500),
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "courses"."level" IS 'BEGINNER: beginner\nINTERMEDIATE: intermediate\nADVANCED: advanced';
COMMENT ON TABLE "courses" IS 'Database model for Educational Courses.';
CREATE TABLE IF NOT EXISTS "course_modules" (
    "id" UUID NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "lessons_count" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "course_id" UUID NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "course_modules" IS 'Module model for courses';
CREATE TABLE IF NOT EXISTS "lessons" (
    "id" UUID NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "type" VARCHAR(8) NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "module_id" UUID NOT NULL REFERENCES "course_modules" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "lessons"."type" IS 'THEORY: theory\nPRACTICE: practice\nVIDEO: video';
COMMENT ON TABLE "lessons" IS 'Lesson model for modules';
CREATE TABLE IF NOT EXISTS "content_blocks" (
    "id" UUID NOT NULL PRIMARY KEY,
    "type" VARCHAR(9) NOT NULL,
    "level" INT,
    "text" TEXT,
    "language" VARCHAR(50),
    "code" TEXT,
    "video_id" VARCHAR(100),
    "src" VARCHAR(255),
    "alt" VARCHAR(255),
    "practice_id" UUID,
    "description" TEXT,
    "task_type" VARCHAR(50),
    "validation_regex" VARCHAR(255),
    "placeholder" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lesson_id" UUID NOT NULL REFERENCES "lessons" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "content_blocks"."type" IS 'HEADING: heading\nPARAGRAPH: paragraph\nCODE: code\nVIDEO: video\nIMAGE: image\nPRACTICE: practice';
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
    "telegram_id" VARCHAR(255) UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users"."role" IS 'STUDENT: student\nTEACHER: teacher\nADMIN: admin';
COMMENT ON TABLE "users" IS 'User model for the educational platform';
CREATE TABLE IF NOT EXISTS "user_courses" (
    "id" UUID NOT NULL PRIMARY KEY,
    "progress" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "status" VARCHAR(11) NOT NULL DEFAULT 'in_progress',
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_accessed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,
    "certificate_id" VARCHAR(100),
    "course_id" UUID NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_course_user_id_80bce0" UNIQUE ("user_id", "course_id")
);
COMMENT ON COLUMN "user_courses"."status" IS 'COMPLETED: completed\nIN_PROGRESS: in_progress';
COMMENT ON TABLE "user_courses" IS 'Model for tracking user progress in courses';
CREATE TABLE IF NOT EXISTS "certificates" (
    "id" UUID NOT NULL PRIMARY KEY,
    "issued_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "certificate_url" VARCHAR(500),
    "user_course_id" UUID NOT NULL UNIQUE REFERENCES "user_courses" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "certificates" IS 'Certificate model for completed courses';
CREATE TABLE IF NOT EXISTS "user_practice_attempts" (
    "id" UUID NOT NULL PRIMARY KEY,
    "answer" TEXT NOT NULL,
    "is_correct" BOOL NOT NULL,
    "feedback" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "practice_id" UUID NOT NULL REFERENCES "content_blocks" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_progress" (
    "id" UUID NOT NULL PRIMARY KEY,
    "completed_lessons" JSONB NOT NULL,
    "completed_practices" JSONB NOT NULL,
    "progress" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "course_id" UUID NOT NULL REFERENCES "courses" ("id") ON DELETE CASCADE,
    "last_accessed_lesson_id" UUID REFERENCES "lessons" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_progre_user_id_45743d" UNIQUE ("user_id", "course_id")
);
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
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
