# Postgres GUI

## Installing ##

Install the dependencies by running:

    pip install -r requirements.txt


## Running ##

To run:

    python app.py


## Compiling ##

(Not working) To compile this into a single file executable use PyInstaller:

    pyinstaller --onefile --windowed --add-data="app.glade:." --add-data="style.css:." app.py


## Features ##

- Connection window for managing and saving connection information
- Uses keyring for storing passwords
- Can connect through SSH tunnel
- Data window shows list of tables on the left
- Can browse through data 20 rows at a time with the ability to filter
- Generic query tab for running any query
