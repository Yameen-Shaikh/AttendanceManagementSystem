# Project Changes

This document summarizes the recent changes made to the project.

## 1. Static Files Consolidation

-   **Merged CSS files:** The contents of `student/static/css/style.css` and `staticfiles/css/style.css` were merged into a single file located at `static/css/style.css`.
-   **Renamed `staticfiles` to `static`:** The `staticfiles` directory was renamed to `static` to adhere to Django's best practices for development static files.
-   **Removed `student/static` directory:** The `student/static` directory was removed to eliminate duplicate static files.

## 2. Django Settings Update

-   **`settings.py` was updated to correctly handle static files:**
    -   `STATICFILES_DIRS` is now set to `[BASE_DIR / 'static']` to tell Django where to find static files during development.
    -   `STATIC_ROOT` is set to `BASE_DIR / 'staticfiles'` which is used to collect all static files for production using the `collectstatic` command.

## 3. Template Cleanup

-   **Removed inline styles:** Inline `<style>` blocks and `style` attributes were removed from `student/templates/base.html`.
-   **Moved styles to CSS file:** The removed styles were moved to the main stylesheet at `static/css/style.css`.
-   **Added `extra_css` block:** A `{% block extra_css %}` was added to the `<head>` of `base.html` to allow for template-specific CSS.

## 4. URL Configuration Cleanup

-   **Added docstrings:** Docstrings were added to `ams/urls.py`, `student/urls.py`, and `teacher/urls.py` to improve code documentation.
-   **Formatted code:** The code in the `urls.py` files was formatted for better readability.

## 5. `README.md` Creation

-   A `README.md` file was created to provide comprehensive information about the project, including:
    -   Project structure
    -   Setup instructions for a new developer
    -   Usage guidelines

## 6. UI Enhancements

-   **Navbar Styling:** The navbar now has a white background, black text, rounded corners, and a subtle box shadow for a clean and modern look.
-   **Glowing Effect:** A glowing effect using the color `#cdd2bf` has been applied to the navbar and all card elements (`.card`, `.login-card`, `.dashboard-card`).
-   **Button Styling:** All buttons in the application now use a gradient style (`.btn-grad`) with a glowing effect on hover.

## 7. Bug Fixes and UI Refinements

### 7.1. `NoReverseMatch` Error for `scan_qr_code`

-   **Problem:** The `student:scan_qr_code` URL was being called without arguments in some places, while its URL pattern expected a `class_id`. This resulted in a `django.urls.exceptions.NoReverseMatch` error.
-   **Diagnosis:**
    -   The `student/urls.py` file defined the `scan_qr_code` URL pattern as `scan-qr/<int:class_id>/`, requiring a `class_id`.
    -   A search revealed that `student/templates/base.html` contained a "Mark Attendance" link that called `{% url 'student:scan_qr_code' %}` without providing the required `class_id`.
-   **Solution:**
    -   Modified `student/urls.py` to ensure the `scan_qr_code` URL pattern correctly accepts a `class_id`.
    -   Updated the `scan_qr_code` view in `student/views.py` to accept the `class_id` parameter and pass it to the template.
    -   Modified `student/templates/student/student_dashboard.html` to correctly pass `enrollment.class_obj.id` to the `scan_qr_code` URL.
    -   Removed the problematic "Mark Attendance" link from `student/templates/base.html` as it was a general navigation link that could not provide a specific `class_id` in its context.

### 7.2. CSS "property value expected" Error and IDE Red Highlighting

-   **Problem:** The user reported a "property value expected" CSS error and their IDE was highlighting `student/templates/student/student_dashboard.html` in red, indicating a syntax issue.
-   **Diagnosis:**
    -   An initial investigation revealed an invalid `rgba` color value in `static/css/style.css` (missing the alpha channel), which was a direct cause of the "property value expected" error.
    -   `student/templates/student/student_dashboard.html` contained an inline `<style>` block, which violated the project's convention of externalizing styles (as documented in `gemini.md`).
    -   A missing closing `</div>` tag was identified within the `{% for %}` loop in `student/templates/student/student_dashboard.html`, leading to HTML parsing errors.
    -   Through a process of simplification and gradual reintroduction of content, the persistent IDE red highlighting was traced to the inline `style="width: ..."` attribute used for the progress bar in `student/templates/student/student_dashboard.html`.
-   **Solution:**
    -   Corrected the invalid `rgba` color value in `static/css/style.css` by adding the missing alpha channel.
    -   Moved the inline `<style>` block from `student/templates/student/student_dashboard.html` to `static/css/style.css` to adhere to project conventions.
    -   Added the missing closing `</div>` tag in `student/templates/student/student_dashboard.html` to fix HTML structure.
    -   Removed the inline `style="width: ..."` attribute from the progress bar in `student/templates/student/student_dashboard.html`.
    -   Implemented a JavaScript solution in `student/templates/student/student_dashboard.html` to dynamically set the width of the progress bar based on a `data-progress` attribute, thus avoiding inline styles.

### 7.3. Button Visibility and Styling

-   **Problem:** After debugging the "red file" error, the "Mark Today's Attendance" button was not properly visible or styled as expected.
-   **Diagnosis:**
    -   The button was inadvertently removed from `student/templates/student/student_dashboard.html` during the debugging process of simplifying the template content.
    -   The `btn-grad` CSS styles in `static/css/style.css` were temporarily simplified to isolate potential conflicts, which affected the button's appearance.
-   **Solution:**
    -   Re-added the "Mark Today's Attendance" button to its correct position within the card in `student/templates/student/student_dashboard.html`.
    -   Reverted the `btn-grad` CSS styles in `static/css/style.css` to their original, full-featured state, restoring the intended gradient and glowing effects.

## 8. Static Files and Theming Separation

-   **Separated Student and Teacher Static Files:** To support different themes for the student and teacher applications, the static files were separated.
    -   The original `static` directory was moved to `teacher/static`.
    -   A new `student/static` directory was created for the student application's styles and assets.
-   **Created a Teacher-Specific Base Template:**
    -   A new `base_teacher.html` was created in `teacher/templates` to serve as the base template for all teacher-facing pages.
    -   All teacher templates were updated to inherit from `base_teacher.html`.
-   **Renamed Teacher's Stylesheet:**
    -   The stylesheet for the teacher application was renamed to `teacher_style.css` to avoid naming conflicts with the student stylesheet.
    -   The `base_teacher.html` template was updated to load `teacher_style.css`.
-   **Updated Django Settings for Static Files:**
    -   The `STATICFILES_DIRS` setting was removed from `settings.py` to allow Django's `AppDirectoriesFinder` to automatically discover the static files in each application's `static` directory. This is the recommended approach for managing app-specific static files.

## 9. Student Application UI/UX Overhaul

-   **New Base Template:** Created a new `base_student.html` template to serve as the foundation for the student-facing pages, enabling a distinct theme for the student application.
-   **Template Inheritance Update:** Updated all relevant student templates to inherit from `base_student.html`, ensuring a consistent application of the new theme.
-   **Template Cleanup:** Removed the unused `base.html` template from the `student` application to maintain a clean and organized codebase.
-   **Video Background:** Implemented a video background in `base_student.html` to create a modern and engaging user experience.
-   **Glass Effect Theme:**
    -   **Navbar:** Styled the navbar with a "glass effect" (translucent with a blur) to match the overall theme. Made the navbar responsive, with rounded corners and margins on larger screens.
    -   **Sidebar:** Applied the glass effect to the off-canvas sidebar for a consistent look and feel.
-   **Improved Layout and Styling:**
    -   **Centered Content:** Vertically centered the main content on all pages to improve the layout and visual balance.
    -   **Button Styling:** Added a gradient button style (`.btn-grad`) for a more prominent and visually appealing call-to-action button.
    -   **Card Spacing:** Removed inline styles from the profile card to ensure consistent and responsive spacing on all screen sizes.

## 10. Student UI & Background Video Enhancements

### 10.1. Background Video Optimization

-   **Optimized Video File:** The background video was optimized for web streaming (`-movflags +faststart`) and a new version (`bg_optimized.mp4`) was added. The old video files were removed or replaced.
-   **Preloading:** Added `<link rel="preload">` for the video in `base_student.html` to prioritize its loading.
-   **Fallback Background Color:** Set a fallback background color (`#010b18`) on the `body` to provide an instant visual feedback while the video is loading.
-   **Video Element Update:** The `<video>` element was updated to use the optimized video file and a class selector (`.bg-video`) for styling.

### 10.2. Mobile Sidebar Adjustments

-   **Positioning:** The offcanvas sidebar for mobile screens was moved from the left to the right side of the screen.
-   **Sizing:** The sidebar width is now set to cover 50% of the viewport width.
-   **Styling:**
    -   Added rounded corners to the sidebar to match the desktop navbar's aesthetic.
    -   The color of the sidebar navigation links was changed to white for better visibility.
-   **Navbar Button:** The hamburger button to toggle the sidebar was moved to the right side of the navbar for better user experience on mobile.

### 10.3. QR Scanner Layout Fix

-   **Responsive Scanner:** Fixed a layout issue on the QR code scanning page where the scanner element was overflowing its container. The width of the scanner is now set to `100%` to ensure it fits within the parent card on all screen sizes.

### 10.4. Other Changes

-   **`ALLOWED_HOSTS`:** Updated an IP address in the `ALLOWED_HOSTS` setting in `ams/settings.py`.

## 11. New Features Implementation

*   **Teacher's Historical Performance Line Chart:**
    *   Added a line chart to the teacher's dashboard to visualize attendance trends for their classes.
    *   Implemented a new view `get_attendance_data` to provide data for the chart.
    *   Used Chart.js to render the chart.

*   **Student's Calendar View and Subject Summary:**
    *   Added a calendar to the student's dashboard to show their daily attendance status.
    *   Used FullCalendar to render the calendar.
    *   Implemented a new view `get_attendance_calendar_data` to provide data for the calendar.
    *   The student dashboard now displays a summary of their attendance record for each subject.

*   **Real-time Notifications:**
    *   Implemented real-time notifications for students when they mark their attendance.
    *   Used Django Channels to handle WebSocket communication.
    *   Created a `NotificationConsumer` to manage WebSocket connections.
    *   Modified the `mark_attendance` view to send notifications.

*   **UI and Navigation:**
    *   Created a new "Reports" page for teachers.
    *   Moved the "Attendance Performance" chart to the "Reports" page.
    *   Added a "Reports" link to the teacher's navbar.
    *   Centered and widened the "Select Class" dropdown on the reports page for better visibility.

*   **Dependencies:**
    *   Added `channels` to `requirements.txt`.
    -   Resolved installation issues with `Pillow` and `psycopg2-binary` by updating `Pillow` and switching to `psycopg2`.

## 12. Student Dashboard and Navigation Enhancements

-   **Student Dashboard Content Refinement:**
    -   The `student/templates/student/student_dashboard.html` was updated to clearly display academic details (course, class, subject, and attendance percentage) for each enrolled class within individual cards.
    -   "Unenroll" and "Enroll" buttons were ensured to consistently use the `btn-grad` styling for a uniform look.

-   **Student Reports Page Implementation:**
    -   A "Reports" link was added to the main navigation bar and the off-canvas sidebar in `student/templates/base_student.html` for student users.
    -   A new template, `student/templates/student/reports.html`, was created. This page integrates Chart.js to visualize the student's attendance performance across their enrolled classes, leveraging the existing `get_attendance_data` view.

-   **Student QR Scan Functionality Enhancement:**
    -   A "Scan" link was added to the main navigation bar and the off-canvas sidebar in `student/templates/base_student.html` for student users.
    -   The `student/urls.py` file was modified to remove the `class_id` parameter from the `scan_qr_code` URL pattern, allowing direct access to the QR scanner.
    -   The `scan_qr_code` view in `student/views.py` was updated to no longer require a `class_id` parameter, simplifying the scanning process for students.

## 13. Teacher Approval Mechanism

*   **Teacher's Historical Performance Line Chart:**
    *   Added a line chart to the teacher's dashboard to visualize attendance trends for their classes.
    *   Implemented a new view `get_attendance_data` to provide data for the chart.
    *   Used Chart.js to render the chart.

*   **Student's Calendar View and Subject Summary:**
    *   Added a calendar to the student's dashboard to show their daily attendance status.
    *   Used FullCalendar to render the calendar.
    *   Implemented a new view `get_attendance_calendar_data` to provide data for the calendar.
    -   The student dashboard now displays a summary of their attendance record for each subject.

*   **Real-time Notifications:**
    *   Implemented real-time notifications for students when they mark their attendance.
    *   Used Django Channels to handle WebSocket communication.
    *   Created a `NotificationConsumer` to manage WebSocket connections.
    *   Modified the `mark_attendance` view to send notifications.

*   **UI and Navigation:**
    *   Created a new "Reports" page for teachers.
    *   Moved the "Attendance Performance" chart to the "Reports" page.
    *   Added a "Reports" link to the teacher's navbar.
    *   Centered and widened the "Select Class" dropdown on the reports page for better visibility.

*   **Dependencies:**
    *   Added `channels` to `requirements.txt`.
    -   Resolved installation issues with `Pillow` and `psycopg2-binary` by updating `Pillow` and switching to `psycopg2`.

## 12. Teacher Approval Mechanism

-   **Problem:** Teachers were able to log in without being approved by an administrator.
-   **Solution:**
    -   Removed the `is_approved` field from the `CustomUser` model.
    -   The `login_view` in `ams/views.py` was modified to only check for the `is_active` flag.
    -   The `teacher_register_view` in `teacher/views.py` was modified to set `is_active` to `False` for new registrations.
    -   The `student/admin.py` was modified to allow administrators to activate users.

## 14. Student Application UX and Feature Enhancements

-   **Student Dashboard UI/UX Overhaul**:
    -   The student dashboard layout has been simplified to feature a single, centered card for a cleaner and more focused user experience.
    -   The course name is now prominently displayed as the title within the card.
    -   A confirmation dialog has been added to the "Unenroll" action to prevent accidental removal from a course.

-   **Sticky Navbar**:
    -   The main navigation bar in the student application is now sticky, ensuring it remains accessible while scrolling through content.

-   **Roll Number for Students**:
    -   An optional `roll_no` field has been added to the `CustomUser` model, allowing students to provide a roll number during registration if available.
    -   The student registration form has been updated to include the new "Roll No" field.

-   **Enhanced QR Code Scanning**:
    -   The class selection dropdown has been removed from the QR code scanning page for a more streamlined workflow.
    -   The application now automatically identifies the class associated with the scanned QR code.
    -   A new validation check ensures that a student is enrolled in the respective class before an attendance record is created.

-   **Styling and CSS Refinements**:
    -   The styling for cards in the student application has been centralized to ensure a consistent look and feel across all pages.
    -   Card and layout styles have been adjusted for improved responsiveness and accurate centering on mobile devices.
    -   The course title on the student dashboard is now styled to be white for better visibility.

## 15. Lecture-Based Attendance Tracking

To enable accurate tracking of missed attendance, a new `Lecture` model was introduced. This provides a definitive record of all scheduled class sessions, against which student attendance is recorded.

-   **New `Lecture` Model:**
    -   A `Lecture` model was created in the `teacher` app to store details of each scheduled class session (class, date, time).
    -   The `Attendance` and `QRCode` models were updated to link directly to a `Lecture` instance, replacing the previous reliance on `class` and `date` fields.
    -   Generated and applied the necessary database migrations.

-   **Enhanced Teacher Workflow:**
    -   Teachers can now schedule individual lectures for their classes via a new "Schedule Lecture" page.
    -   A "View Lectures" page was added, listing all scheduled lectures for a class.
    -   QR code generation is now tied to a specific lecture instance, initiated from the lecture list.

-   **Updated Student Workflow:**
    -   The attendance marking process was updated to create an `Attendance` record linked to the specific `Lecture` that was scanned.
    -   The QR code scanning page (`scan_qr.html`) was improved to show scan results (success or error) in a pop-up modal for a cleaner user experience.

-   **Accurate Reporting:**
    -   Attendance percentage calculations in both the student dashboard and teacher reports were updated to be based on the total number of scheduled lectures versus attended lectures.

-   **Data Pruning Feature:**
    -   To manage database growth, a feature was added for teachers to delete old lecture records.
    -   This is accessible via a "Delete old lectures" button on the lecture list page, which reveals a collapsible card with a form to specify the age of records to prune.
    -   The logic is handled in a new `prune_lectures_view` and is scoped to the teacher's own classes for security.
    -   A corresponding management command `prune_lectures` was also created for potential CLI-based or scheduled cleanup.

-   **UI/UX Refinements:**
    -   The lecture list page (`view_lectures.html`) was refined through several iterations to achieve a wide, single-column layout where the pruning options appear below the main card.
    -   Fixed a CSS issue in `teacher_style.css` where a fixed card width was preventing responsive layouts.

## 16. Teacher UI Enhancements

- **Reports Page:**
    - Widened the class selection dropdown on the reports page for better visibility.
    - Moved the inline styles to the `teacher_style.css` stylesheet.
- **Button Styling:**
    - Standardized button styles across the teacher dashboard, schedule lecture, and view lectures pages to use the `btn-primary` class for a consistent look and feel.
- **Navigation:**
    - Removed the "View Report" button from the teacher dashboard to streamline the UI.

## 17. Course and Class Management Refactor

-   **Refactored Course, Class, and Subject Management:**
    -   Moved the responsibility of creating and managing `Courses` and `Classes` from teachers to administrators to ensure data consistency.
    -   Removed the ability for teachers to create, update, or delete courses and classes.
    -   Introduced a new `Subject` model to link teachers to the classes they teach. A teacher now creates subjects for a specific class.
    -   Updated the database schema with a new migration to reflect these changes.
-   **New Teacher Workflow:**
    -   Created a "Select Class" page where teachers can browse all available courses and classes.
    -   From the "Select Class" page, teachers can add subjects to the classes they teach.
    -   The teacher dashboard has been updated to display the subjects taught by the teacher, grouped by course and class.
-   **Admin Panel Enhancements:**
    -   The `Class` creation form in the admin panel now only shows `name` and `course` fields.
    -   Added placeholders to input fields in the admin panel for `Course`, `Class`, `Subject`, and `CustomUser` models to improve usability.
-   **Improved Login Experience:**
    -   The login error message for teachers pending approval has been updated to "Invalid username or password/Approval pending." for better clarity.

## 18. Teacher Dashboard and UI Refinements

-   **Teacher Dashboard Layout Refinement:**
    -   The "My Subjects" title is now centered within the card header.
    -   Nested cards for individual classes within courses have been removed, simplifying the layout. Class names and their subjects are now displayed directly within the main card body.
    -   The "Add Subject" button has been moved from the `card-footer` to the `card-body`, is now centered, and has a top margin for better visual separation.
    -   The overall width of the main dashboard card has been increased for better content fit.
-   **Select Class Page:**
    -   The entire content of the "Select Class" page is now placed within a card, creating a more consistent and visually appealing layout.
    -   Removed an unnecessary inline style block from the template.
-   **Styling:**
    -   Removed the `text-shadow` from the `.gradient-title` class in `teacher_style.css`.

## 19. Subject-Specific Lecture Management

To allow teachers to differentiate lectures by subject and generate QR codes for specific subjects, the lecture management system has been significantly updated:

-   **`Lecture` Model Update:**
    -   The `Lecture` model (`teacher/models.py`) now links directly to a `Subject` instead of a `Class`. This change was implemented with a database migration. The `subject` field is currently nullable to facilitate data migration, but it is intended to be non-nullable in the future.
-   **Updated Views (`teacher/views.py`):**
    -   `schedule_lecture_view`: Modified to accept `subject_id` instead of `class_id`, ensuring lectures are scheduled for specific subjects.
    -   `view_lectures`: Modified to accept `subject_id`, allowing teachers to view lectures for a particular subject.
    -   `prune_lectures_view`: Updated the filtering logic to prune lectures based on the `subject` taught by the current teacher.
    -   `generate_qr_code`: The permission check now verifies if the teacher teaches the `subject` associated with the lecture.
    -   `get_attendance_data`: Modified to accept `subject_id`, providing attendance data specific to a subject.
    -   `view_report`: Modified to accept `subject_id`, generating attendance reports for a specific subject.
    -   `reports_view`: Updated to correctly populate the context for the `reports.html` template, ensuring subjects are available for each class.
-   **Updated URL Patterns (`teacher/urls.py`):**
    -   URL patterns for `schedule_lecture`, `view_lectures`, `get_attendance_data`, and `view_report` were updated to use `subject_id` in their paths.
-   **Updated Templates:**
    -   `teacher/templates/teacher/schedule_lecture.html`: Modified to display the subject name and its associated class name.
    -   `teacher/templates/teacher/view_lectures.html`: Modified to display the subject name and its associated class name.
    -   `teacher/templates/teacher/teacher_dashboard.html`: The "Schedule Lecture" and "View Lectures" buttons now correctly pass `subject.id` and display the subject name for clarity.
    -   `teacher/templates/teacher/reports.html`: Updated to use a "Select Subject" dropdown and pass `subject.id` to the `get_attendance_data` function for subject-specific attendance charts.

## 20. QR Code and Attendance Workflow Refinements

This series of changes addresses bugs and improves the logic related to QR code generation and attendance marking.

-   **Fixed "Already Marked" Bug:**
    -   **Problem:** Students would scan a new QR code but receive an "Attendance already marked" error if they had already marked attendance for that same lecture on a previous day.
    -   **Diagnosis:** The `mark_attendance` view was correctly preventing duplicate attendance records for the *same lecture instance*. The workflow issue was that teachers were reusing a single lecture instance for multiple days.
    -   **Solution:** The `mark_attendance` view was refactored to use `get_or_create`. This makes the process more robust. It now provides a consistent success message ("Attendance marked for {subject}") whether the attendance is new or was already recorded, avoiding user confusion while still preventing duplicate data entries.

-   **Fixed QR Code Regeneration Crash:**
    -   **Problem:** Generating a QR code for a lecture that had a previous (even expired) QR code would cause a database `IntegrityError`.
    -   **Diagnosis:** The `lecture` field on the `QRCode` model was a `OneToOneField`, enforcing a rule that a lecture could only ever have one QR code in its lifetime.
    -   **Solution:** The field was changed from a `OneToOneField` to a `ForeignKey`, correctly modeling that a lecture can have a history of multiple QR codes. A database migration was created and applied to enact this schema change.

-   **Prevented QR Code Generation for Past Lectures:**
    -   **Problem:** The system allowed teachers to generate QR codes for lectures scheduled on previous dates, which is not a valid workflow.
    -   **Solution:** Logic was added to the `generate_qr_code` view to check if the lecture's date is in the past. If it is, the system now shows an error message ("You cannot generate a QR code for a past lecture.") and prevents the code from being generated.

-   **Added CLI Helper Commands:**
    -   To assist with development and debugging, two new management commands were created:
        -   `python manage.py list_classes`: Lists all courses and their associated classes with their IDs.
        -   `python manage.py get_subjects --class_id <ID>`: Lists all subjects for a given class ID.

## 21. Academic Session Management and Historical Data

To support multiple academic years and preserve historical records, the application's data model and logic were fundamentally updated.

-   **Data Model Changes:**
    -   **`AcademicSession` Model:** A new model was created in `teacher/models.py` to define distinct academic periods (e.g., "2025-2026"), each with a start date, end date, and an `is_active` flag.
    -   **`Class` Model Update:** The `Class` model was linked to `AcademicSession` via a non-nullable foreign key, ensuring every class belongs to a specific session.
    -   **Data Integrity:** The `on_delete` property for `Attendance.lecture` was set to `SET_NULL`, preventing attendance records from being deleted if a lecture is pruned.
    -   **Proxy Model for Reporting:** A proxy model, `HistoricalAttendance`, was created to provide a dedicated view in the admin panel for historical data without altering the original `Attendance` model.

-   **Session-Aware Application Logic:**
    -   **Teacher and Student Views:** All relevant views in both the `teacher` and `student` apps were updated to be "session-aware." They now filter all data (classes, subjects, reports, etc.) based on the currently active `AcademicSession`.
    -   **User Experience:** The UI now only presents users with options and data relevant to the current academic year, preventing confusion and errors like enrolling in a class from a past session. Error handling was added for cases where no active session is configured.

-   **Administrator Historical Data Review:**
    -   **Django Admin Integration:** Instead of a new interface, the existing Django Admin panel was enhanced.
    -   **Session Management:** Administrators can now manage academic sessions directly from the admin panel, including creating new sessions and activating/deactivating them.
    -   **Historical Attendance View:** A new "Historical Attendance Records" section is available in the admin panel. This read-only view allows admins to easily filter all attendance records by academic session, subject, or student, providing a powerful tool for reviewing past data.

## 22. Teacher Manual Attendance

To handle cases where students cannot scan a QR code, teachers can now mark attendance manually.

-   **New Feature:**
    -   A "Manual Attendance" section was added to the QR code generation page (`teacher/generate_qr.html`).
    -   This provides teachers with a search bar to find students in their class by name or roll number.
-   **Interactive UI:**
    -   The search results are displayed dynamically on the page without a reload.
    -   Each student in the results has a "Mark Present" button. The button is disabled if the student's attendance has already been marked.
    -   Clicking the button marks the student as present and provides immediate visual feedback to the teacher.
-   **Backend Implementation:**
    -   Two new API endpoints were created: `search_students` to fetch student data and `manual_mark_attendance` to record the attendance.
    -   These views use AJAX to provide a seamless user experience.
-   **UI Refinements:**
    -   The QR code and manual attendance features were consolidated into a single, full-width card for a cleaner and more unified "Live Lecture Panel."

## 23. Email Confirmation for Attendance

- **New Feature:**
    - Implemented a feature to send a confirmation email to students when their attendance is marked.
- **Implementation Details:**
    - Created a new `email.py` file in the `student` app to handle the email sending logic.
    - Added a new template `student/templates/student/email/attendance_confirmation.txt` for the email body.
    - The `mark_attendance` view in `student/views.py` and the `manual_mark_attendance` view in `teacher/views.py` were updated to call the email sending function.
- **Configuration:**
    - The `EMAIL_BACKEND` in `ams/settings.py` is set to `django.core.mail.backends.console.EmailBackend` for development.
    - Added commented-out settings for production email configuration using SMTP.

## 24. Reporting UI and Charting Refinements

- **Report Page Overhaul:**
    - The report pages for both students and teachers were updated to provide a more focused and clear presentation of attendance data.
    - Removed the "My Attendance Trend" line chart from the student reports page and the "Student Attendance Percentage" bar chart from the teacher reports page to simplify the UI.
- **Pie Chart Implementation:**
    - Both report pages now feature a primary pie chart that displays the distribution of "Attended" vs. "Missed" lectures (for students) or "Present" vs. "Absent" statuses (for teachers) for a selected subject.
    - The backend views (`get_student_subject_attendance_data` and `get_teacher_subject_attendance_data`) were created or updated to supply the necessary data for these pie charts.
- **Bug Fix & UX Improvements:**
    - **Chart.js Dependency:** Fixed a bug on the student reports page where the chart would not render because the Chart.js library was not included. It has been added to the `base_student.html` template.
    - **Auto-Selection:** The student reports page now automatically selects the first subject in the dropdown menu, allowing the chart to load immediately without user interaction.
    - **Layout Adjustments:**
        - The height of the chart on the student reports page was reduced to prevent the card from becoming scrollable on smaller screens.
        - The card and the subject-selection dropdown on the teacher reports page were made full-width to provide a more spacious layout.