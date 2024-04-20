# Organization
This section outlines the repository's file structure.

## app.py
- **Purpose**: The entry point to run the application.

## x
- **Description**: Houses the Pythonic wrapper for the X API. 
- **Note**: Feel free to add new files to prevent the wrapper file from becoming overly lengthy.
    - **wrapper.py**: Implements the `XWrapper` class.

## ai
- **Description**: Contains the logic and system for the AI agent.

## data
- **Description**: Hosts databases and data models essential for the application.
    - **database.py**: Features an abstract base class for the database and a concrete SQLite implementation.
    - **types.py**: Defines types that are not models.
    - **models**: Stores the data models utilized in the application, with each model corresponding to a table in the SQLite database.
        - **user.py**: User data model.
        - 

