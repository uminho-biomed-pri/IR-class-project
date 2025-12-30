# InfRetr

## Overview
InfRetr is a project for information retrieval and processing.

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
git clone <repository-url>
cd InfRetr
pip install -r requirements.txt
```

## Usage
```python
# add your usage instructions here
```

## Features
- Efficient information retrieval
- Easy-to-use API
- Scalable architecture

## Scraper

Why BeautifulSoup is not used? 

- For Angular/React/Vue apps, you need JavaScript execution, which BeautifulSoup cannot provide.

Current approach uses Selenium, which:

- Launches a real browser (Chrome)
- Executes JavaScript
- Waits for Angular to fetch and render data (WebDriverWait, time.sleep)
- Then extracts content from the fully-rendered DOM

Notice that code specifically waits for Angular components. 

Alternatives to Selenium (If you want lighter-weight solutions):

- Playwright - faster, more modern than Selenium
- API inspection - Angular apps often fetch data from JSON APIs you could call directly (check Network tab in DevTools)
- Puppeteer (Node.js) - similar to Selenium but lighter

## Contributing
Contributions are welcome. Please submit a pull request.

## License
MIT License

## Contact
For questions, open an issue in the repository.