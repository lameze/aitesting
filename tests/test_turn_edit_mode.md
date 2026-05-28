# Test: Moodle Login

## Preconditions
- A Moodle site is accessible
- A valid teacher account exists

## Steps
1. Navigate to the Moodle site homepage
2. Enter username: "t1"
3. Enter password: "test"
4. Click the "Log in" button
5. Click the "course1" link
7. Find the edit mode form near the top right of the page (it posts to /editmode.php).
   Inside it there is a checkbox input with name="setmode". Click that checkbox to turn edit mode ON.
   Wait for the page to reload and confirm that editing controls (e.g. "Add an activity or resource" links) are now visible before continuing.

## Expected Results
- Verify that the edit mode has been turned on and editing controls are visible on the page
- A screenshot is captured as evidence of the final state
