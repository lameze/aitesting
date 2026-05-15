# Test: Drag and Drop Activity on Course Page

## Preconditions
- A Moodle site is accessible
- A valid teacher account exists
- The "Activity examples" course exists with an "Online text assignment" activity and a "Choices" section

## Steps

### Login
1. Navigate to the Moodle site homepage
2. Click the "Log in" link
3. Enter username: "teacher"
4. Enter password: "moodle"
5. Click the "Log in" button

### Navigate to course
6. On the "My courses" page, click the "Activity examples" course link

### Enable edit mode
7. Find the edit mode form near the top right of the page (it posts to /editmode.php).
   Inside it there is a checkbox input with name="setmode". Click that checkbox to turn edit mode ON.
   Wait for the page to reload and confirm that editing controls (e.g. "Add an activity or resource" links) are now visible before continuing.

### Drag and drop activity
8. Locate the "Online text assignment" activity on the course page
9. Drag the "Online text assignment" activity and drop it onto the "Choices" section

### Evidence
10. Take a screenshot of the course page showing the final state

## Expected Results
- The user is logged in successfully and "Hi, Terri!" is displayed
- The "Activity examples" course page is visible in edit mode
- The "Online text assignment" activity is now listed inside the "Choices" section
- No error messages are visible on the page
- A screenshot is captured as evidence of the final state
