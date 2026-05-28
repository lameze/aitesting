# MDLQA-45: A teacher can display choice responses horizontally or vertically

## Preconditions
- A Moodle site is accessible
- A course exists with a teacher and at least one student enrolled
- A choice activity exists in the course with the following settings already configured:
  - "Publish results" is set to "Show results to students after they answer"
  - "Privacy of results" is set to "Publish anonymous results, do not show students names"
- At least one student has already responded to the choice activity

---

## Part 1: Set display mode to Vertical (as Teacher)

### Login as teacher
1. Navigate to the Moodle site homepage
3. Enter username: "teacher"
4. Enter password: "moodle"
5. Click the "Log in" button
6. Verify the teacher is logged in (name appears in the top navigation bar)

### Enable edit mode and open the choice activity settings
7. Navigate to the course that contains the choice activity
8. Find the edit mode form near the top right of the page (it posts to /editmode.php).
   Inside it there is a checkbox input with name="setmode". Click that checkbox to turn edit mode ON.
   Wait for the page to reload and confirm that editing controls are now visible before continuing.
9. Locate the choice activity on the course page and click its "Edit" link, then select "Edit settings" from the dropdown menu

### Set display mode to Vertical
10. On the activity settings page, locate the field labelled "Display mode for the options"
11. Set it to "Display vertically"
12. Click the "Save and display" button
13. Take a screenshot of the results page as evidence

### Verify vertical display (teacher view)
14. Verify that the choice response options are displayed in vertical order (stacked top to bottom)
15. Take a screenshot to evidence the vertical layout

---

## Part 2: Verify vertical display (as Student)

### Log out and log in as student
16. Log out of the teacher account (click the user menu in the top right and select "Log out")
17. Click the "Log in" link
18. Enter username: "student"
19. Enter password: "moodle"
20. Click the "Log in" button
21. Verify the student is logged in

### Access the choice activity and verify vertical bar chart
22. Navigate to the same course and open the choice activity
23. Verify that the bar chart for the choice responses is displayed vertically (bars stacked top to bottom)
24. Verify that student names and their corresponding choices are NOT displayed on the bar chart
25. Take a screenshot as evidence of the vertical bar chart without student names

---

## Part 3: Set display mode to Horizontal (as Teacher)

### Log out and log in as teacher again
26. Log out of the student account
27. Click the "Log in" link
28. Enter username: "teacher"
29. Enter password: "moodle"
30. Click the "Log in" button
31. Verify the teacher is logged in

### Update the choice activity to display horizontally
32. Navigate to the course that contains the choice activity
33. Find the edit mode form near the top right of the page (it posts to /editmode.php).
    Inside it there is a checkbox input with name="setmode". Click that checkbox to turn edit mode ON.
    Wait for the page to reload and confirm that editing controls are now visible before continuing.
34. Locate the choice activity and click its "Edit" link, then select "Edit settings"
35. On the activity settings page, locate the field labelled "Display mode for the options"
36. Set it to "Display horizontally"
37. Click the "Save and display" button

### Verify horizontal display (teacher view)
38. Verify that the choice response options are displayed in horizontal order (side by side)
39. Take a screenshot to evidence the horizontal layout

---

## Part 4: Verify horizontal display (as Student)

### Log out and log in as student
40. Log out of the teacher account
41. Click the "Log in" link
42. Enter username: "student"
43. Enter password: "moodle"
44. Click the "Log in" button
45. Verify the student is logged in

### Access the choice activity and verify horizontal bar chart
46. Navigate to the same course and open the choice activity
47. Verify that the bar chart for the choice responses is displayed horizontally (bars side by side)
48. Verify that student names and their corresponding choices are NOT displayed on the bar chart
49. Take a screenshot as final evidence of the horizontal bar chart without student names

---

## Expected Results

- After setting "Display vertically":
  - ✅ Teacher sees choice options stacked vertically on the results page
  - ✅ Student sees a vertical bar chart for the responses
  - ✅ No student names or individual choices are visible on the bar chart

- After setting "Display horizontally":
  - ✅ Teacher sees choice options displayed side by side (horizontally) on the results page
  - ✅ Student sees a horizontal bar chart for the responses
  - ✅ No student names or individual choices are visible on the bar chart

