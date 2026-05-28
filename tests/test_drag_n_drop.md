# Test: Drag and Drop Activity on Course Page

## Steps
1. Navigate to the Moodle site homepage
3. Enter username: "admin"
4. Enter password: "test"
5. Click the "Log in" button
6. Click the "course1" link
7. Find the edit mode form near the top right of the page (it posts to /editmode.php).
   Inside it there is a checkbox input with name="setmode". Click that checkbox to turn edit mode ON.
   Wait for the page to reload and confirm that editing controls (e.g. "Add an activity or resource" links) are now visible before continuing.

### Drag and drop activity
8. Locate the "MDLQA-20705" activity on the "General" section on the course1 page
9. Drag the "MDLQA-20705" activity and drop it onto the following section "29 May - 4 June" using **only native browser drag-and-drop interactions** (e.g. mouse down, drag, and mouse up / the playwright `dragTo` method or equivalent pointer event simulation).
   > **DO NOT use the "Edit → Move" menu option or any other UI menu/context-menu approach to move the activity. The purpose of this test is to validate the native drag-and-drop functionality in the browser. If drag-and-drop is not working, report the failure — do not fall back to any menu-based alternative.**

### Evidence
10. Take a screenshot of the course page showing the final state

## Expected Results
- The "MDLQA-20705" activity is now listed inside the "29 May - 4 June" section
- No error messages are visible on the page
- A screenshot is captured as evidence of the final state
