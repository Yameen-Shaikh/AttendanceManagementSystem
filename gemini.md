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
