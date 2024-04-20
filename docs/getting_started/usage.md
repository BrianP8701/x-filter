# Usage
This document outlines two primary ways to use the application:

1. **Hosting the Application**: Run `uvicorn x_filter.app:app --reload` to start the app.

2. **Sending Events**: Utilize the provided script within the `scripts` directory to simulate sending events to the application.

Should you need to edit the documentation, feel free to make changes. Please ensure that any additions or relocations of files within the documentation are accurately reflected in the `mkdocs.yml` file, specifically within the `nav` attribute. To run the documentation locally with ease, execute `mkdocs serve`. Note: If you encounter issues with Cairo despite it being installed, running `export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib:/opt/homebrew/lib` in the terminal typically resolves the problem.
