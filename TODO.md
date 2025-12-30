# TODO List

## High Priority
- [ ] Check if the Chrome binary path is valid before running
- [ ] Implement retry logic for transient failures (network issues, timeouts, etc.)
- [ ] Add config file for handle, max items, output file, etc.

## Features to Implement
- [ ] Futures based on https://github.com/maladeep/Coventry-PureHub-Search-Engine/tree/main?tab=readme-ov-file#features
- [ ] Write directly to JSON file while scraping to save memory on large collections
- [ ] Add Debug mode to enable/disable logging with print statements
- [ ] Implement graphical user interface (GUI) (using Tkinter or PyQt or web-based)
- [ ] Pipeline integration

## Testing
- [ ] Write unit tests for the scraper class

## Notes
- Consider using a configuration library like `configparser` or `python-dotenv` for the config file
- For retry logic, consider using the `tenacity` library