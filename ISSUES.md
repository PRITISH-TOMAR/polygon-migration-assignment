# Issues Analysis
I have modified the code branch-wise: each fix is implemented in a separate branch. So, along with each issue, a **Reproducible on** line is attached, which gives the branch name where the issue can still be reproduced.

## Summary

| Type | Critical | High | Medium | Low | Total |
|------|----------|------|--------|-----|-------|
| Product Issues | 0 | 1 | 1 | 1 | 3 |
| Code Issues | 1 | 1 | 1 | 0 | 3 |

---

## Product Issues

> Product issues are user-facing problems: broken functionality, missing validation, poor UX, data integrity risks visible to users.

---

### [P1] Test cases in DB and S3 may come from different versions of the problem

**Reproducible on**: `main` end to end (the S3 upload works here). Apart from adding AWS S3 support and the upload-order fix, the logic is unchanged from the original code.

**Severity**: High

**Location**: `problems/views.py` ("Migrate Test Description to Database" and "Upload Test Cases" handlers in `index`)

**Description**:
A problem is fetched from Polygon and its test cases are uploaded to S3, but not saved to the DB. Then a new version of the problem, with a different number of test cases, is fetched, and only the DB test case migration is done. Both versions have different test case data and counts.

**Impact**:
Users might see inconsistencies between the stored (DB) and uploaded (S3) data.

**Suggested Fix**:
Add an ordered workflow to keep the data consistent; a version comparison can also be done.

**Priority rationale**:
This is the highest-priority issue because the database and S3 can end up containing test cases from different versions of the same problem.

---


### [P2] Problem statement, Input, Output in HTML format

**Reproducible on**: `main` (the latest code, with all changes made).
**Severity**: Medium

**Location**: `problems/views.py` (`parse_problem_html`), `problems/templates/problems/index.html` (problem statement, input, output and notes display)

**Description**:
All of the Input, Output and Legend (problem statement) appear in HTML format, which is unreadable and does not look good.

**Impact**:
Users find it difficult to understand the statement and the input and output formats.

**Suggested Fix**:
The HTML can be converted to a readable format, for example by converting it to Markdown and rendering that correctly on the page.

**Priority rationale**:
This is mainly a readability issue, so it has a lower priority than issues that affect functionality or data consistency.

---

### [P3] Adding tags misbehaves, and tags are not fetched from Polygon

**Reproducible on**: `original-with-migration` (commit `ad5fc1e`) and `main` (unchanged).

**Severity**: Low

**Location**: `problems/templates/problems/index.html` (tag search input), `problems/views.py` (tag list in `index`), `problems/polygon_api.py` (no Polygon tag fetch)

**Description**:
The default tags of problems on Polygon are not fetched. Also, creating a new tag requires a double click and does not work by pressing Enter.

**Impact**:
Users are unable to figure out how to add a tag unless they double-click.

**Suggested Fix**:
Enable adding a new tag with a single click or by pressing Enter on the keyboard.

**Priority rationale**:
This is a minor UI issue. Adding tags is still possible, but the current interaction is confusing.

---

## Code Issues

> Code issues are technical problems: bugs, security vulnerabilities, performance problems, code quality concerns, architectural issues.

### [C1] Crash when fetching a problem

**Reproducible on**: `original-starter` (commit `7e73f65`) on a fresh database. Fixed by commit `ad5fc1e` (`add-missing-migration`), included in `main`.

**Severity**: Critical

**Location**: `problems/models.py` (`Problem.notes`, `Problem.genie_chat`), `problems/migrations/0001_initial.py` (no columns for these fields)

**Description**:
Following the documented setup (`migrate` → `createsuperuser` → `runserver`) on a fresh database, then clicking **Fetch Problem**, crashes the page with `ProgrammingError: column problems_problem.notes does not exist`. The cause is a missing migration.

**Impact**:
High impact for users, as the entire functionality is broken without this fix.

**Suggested Fix**:
The fix is already implemented (commit `ad5fc1e`) by adding the missing migration, which adds the two columns to the `problems_problem` table.

**Priority rationale**:
Without this migration, fetching a problem fails on a fresh database, making the feature unusable until the migration is applied.
---

### [C2] Entire S3 storage for the problem is deleted before uploading new test cases

**Reproducible on**: `feature/aws-s3-storage` (S3, same order as the original). Original Azure code: `original-with-migration` (`AzureBlobManager.empty_blob` before uploading). Fixed on `main` by branch `fix/upload-before-delete`.

**Severity**: High

**Location**: `problems/polygon_api.py` (`migrate_to_azure_blob`: delete all files first, then upload), `problems/AzureTestcase.py` (`empty_blob`)

**Description**:
When a problem is re-fetched from Polygon and its test cases are uploaded to storage, the function first empties the entire corresponding folder and then refills it with the new test cases. In case of a network failure or similar, the new test cases may not all be written, while the old ones are already gone.

**Impact**:
This introduces inconsistency between the test cases in the database and the test cases uploaded to cloud storage.

**Suggested Fix**:
Already implemented on `main` by branch `fix/upload-before-delete`. The change is to upload all new files first (overwriting same-named ones), and only after every upload succeeds, delete the leftover files that are no longer part of the new set.

**Priority rationale**:
This is less severe than a complete feature failure, but an interrupted upload can leave the stored test cases incomplete.

---

### [C3] Storage was hard-wired to Azure

**Reproducible on**: `original-with-migration`. Addressed on `main` by the storage interface (branch `feature/aws-s3-storage`).

**Severity**: Medium

**Location**: `problems/views.py` (Azure settings read and passed in `index`), `problems/polygon_api.py` (`migrate_to_azure_blob`, `upload_custom_checker_to_azure`), `problems/AzureTestcase.py` (`AzureBlobManager`)

**Description**:
The backend code is hard-wired to Azure, so using another cloud provider for storage requires a lot of changes.

**Impact**:
It will not impact users directly, but developers will have to make significant changes to add a new storage provider.

**Suggested Fix**:
Already implemented by adding a storage factory, on branch `feature/aws-s3-storage`.

**Priority rationale**:
This doesn't directly affect users, but supporting another storage provider would require changes across several parts of the code.

---

## Edge Case Analysis

### Q1

> A Polygon problem has 0 sample test cases but 15 regular test cases. What happens when you migrate this problem?

Tested on `feature/aws-s3-storage`

I might be missing something, but I couldn’t find anything unexpected here. The migration completes successfully, and all 15 test cases are uploaded to cloud storage. When “Migrate Test Description to Database” is clicked, they’re saved as `ProblemTestCase` rows with `is_sample=False`. No `SampleTestCase` rows are created.

So, the sample section on the problem page remains empty, but all 15 test cases are present in both the database and cloud storage.

---

### Q2

> A problem is migrated with 20 test cases. Later, the problem setter removes 8 test cases on Polygon (now 12 remain). The problem is re-migrated. What happens?

Tested on `feature/aws-s3-storage`. The storage step there behaves like the original code (delete everything, then upload). The database steps are unchanged from the original.

Cloud storage is handled correctly: on re-migration the code deletes all existing files under `test_cases/<id>/` and uploads the current 12, so storage ends up with exactly 12 test files.

The database is **not** cleaned up correctly. "Migrate Test Description to Database" matches rows by position. It updates rows 1–12 with the new data, but rows 13–20 from the first run are never deleted. The `Problem` record reports `test_case_count = 12` (updated by "Create/Update problem in Database"), while the database ends up with 20 rows for a problem that now has 12 tests — rows 13–20 contain stale data from the first migration.

---

### Q3

> Two different Polygon problems have the exact same title: "Two Sum". You migrate the first one successfully. Then you try to migrate the second one. What happens?

The second migration fails because of a duplicate slug. In `views.py` (line 298), the slug is generated directly from the title using Django's `slug = slugify(title)`. Since both problems are titled “Two Sum,” they end up with the same slug, `two-sum`.

Tested with two different Polygon problems titled “Guess the Number” (slug `guess-the-number`); the mechanism is the same for “Two Sum”.

The `slug` field in `Problem` (`models.py:58`) has a unique constraint, so the database rejects the second insert with an `IntegrityError`.

The page displays: “Migration failed and all changes have been rolled back. Reason: duplicate key value violates unique constraint "problems_problem_slug_key" DETAIL: Key (slug)=(guess-the-number) already exists.”

No record is created for the second problem, and the first problem’s data remains unaffected.

---

### Q4

> When test cases are saved to the database via "Migrate Test Cases to DB", some data is intentionally discarded. What data is lost? Why might this cause problems?

I found two issues with how test cases are migrated:

1. **(Code reading)** Input and output are truncated to 260 characters (`views.py:540–541`). The code uses `input_data[:260]`, which limits characters, not bytes, despite what the comment says. Longer test cases are stored incompletely, so comparisons against the full files in cloud storage can produce different results.

So, for real verification of a submission, it must be done against the test case data in cloud storage.

2. **(Tested, see Q2)** Old test cases are never deleted during re-migration. The code updates existing rows by position and inserts new ones, but doesn't remove rows beyond the new test count. If a problem previously had more test cases, the extra rows remain in the database, even if they no longer exist on Polygon.

---