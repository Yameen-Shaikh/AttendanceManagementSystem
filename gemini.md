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
    *   Resolved installation issues with `Pillow` and `psycopg2-binary` by updating `Pillow` and switching to `psycopg2`.

## 12. Teacher Approval Mechanism

-   **Problem:** Teachers were able to log in without being approved by an administrator.
-   **Solution:**
    -   Removed the `is_approved` field from the `CustomUser` model.
    -   The `login_view` in `ams/views.py` was modified to only check for the `is_active` flag.
    -   The `teacher_register_view` in `teacher/views.py` was modified to set `is_active` to `False` for new registrations.
    -   The `student/admin.py` was modified to allow administrators to activate users.
