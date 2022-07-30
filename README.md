# Pioneering Pandora Dev-Kit

This is the dev-kit for [Pioneering Pandora](http://pandora.pravega.org/).
Please file bug reports either by using the [contact form](http://pandora.pravega.org/contact),
or by [submitting an issue](https://github.com/Lord-of-the-Galaxy/Pandora-Dev-Kit/issues/new).

## Downloading and Installing

Download `pandora-dev-kit.zip` from the latest [release](https://github.com/Lord-of-the-Galaxy/Pandora-Dev-Kit/releases)
and extract.  

The dev-kit has currently been tested on Python 3.10 only, but is expected to work with Python 3.7+. 
It is recommended you create a separate venv for testing your bots by using `python -m venv venv`
(refer to the [official documentation](https://docs.python.org/3/library/venv.html) for more information on venv). 
Activate the venv (`venv\Scripts\activate` on Windows) and install all prerequisites by running
`pip install -r requirements.txt`.

## Using the Dev-Kit

The dev-kit comes with a few sample games (in `game_logs`).
To view these, and any games you run, first run the command `python server.py`
and then open [localhost:8000](http://127.0.0.1:8000/) to see a list of all available games. 
To run your own games, run `python main.py`.
You can then view the game (assuming it has been logged) by following the previous instructions.
Please check the [Wiki](https://github.com/Lord-of-the-Galaxy/Pandora-Dev-Kit/wiki) for more information.