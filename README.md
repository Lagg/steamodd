# Steamodd

Steam odds and ends

## What is this?

Steamodd is a comprehensive Python library designed to interface with the Steam API, providing a simplified and easy to use set of tools for developers to access and manage the Steam API.

- **Steam API interface wrappers**: Interact with the various endpoints of the Steam API.
- **Steam inventory manager (SIM)**: Manage and manipulate Steam user inventory data.
- **VDF serializer**: Convert Valve Data Format (VDF) files to Python dictionaries and vice versa.

## Requirements

- Python 3+

## Installation

Install via pip for easy access (ideally within a virtual environment):

```sh
$ pip install steamodd
```

For manual installation, use the standard setuptools module:

```sh
$ python setup.py install
```


## How do I use this?

After installation, you can import `steamodd` into your Python project and start interacting with the Steam API. Make sure to have a valid Steam API key for actions that need authentication.

### Fetching a User's Game Library

```python
from steam.api import interface

# Fetch games of user with id 76561198017493014 and include all application information
games = interface('IPlayerService').GetOwnedGames(steamid=76561198017493014, include_appinfo=1)

# Accessing game count
print(games['response']['game_count'])  # Output: 249
```

### Working with Steam Apps

```python
from steam.apps import app_list

apps = app_list()
# Check if a game is in the app list
print('Dota 2' in apps)  # Output: True
```

### Items and Inventory Handling

```python
from steam.items import inventory, schema

# Fetching inventory for a given app id, e.g., Dota 2 with id 570
inv = inventory(76561198017493014, 570)

# Iterating over inventory items
for item in inv:
    print(item.name)

# Fetching and working with item schema
item_schema = schema(440)  # Team Fortress 2
for item in item_schema:
    if item.name == 'Defiant Spartan':
        print(item.type)  # Output: 'Hat'
```

## Documentation

For more detailed information and advanced usage, refer to the [full documentation](http://steamodd.readthedocs.org/en/latest/).

## Testing

To run the test suite, execute the following command:

```sh
python setup.py run_tests -k YOUR_STEAM_API_KEY
```

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please send a pull request.

## Bugs and Feature Requests

Encountered a bug or have a feature idea? Open an [issue](https://github.com/Lagg/steamodd/issues) on GitHub.

