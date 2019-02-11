# QT5 HTML TO PDF
Generate PDF from web pages using QT5

### tl;dr
```sh
# Save the Wikipedia page for "Roland TR-808" to roland.pdf
docker run -i --rm datasense/wkqt5htmltopdf "https://en.wikipedia.org/wiki/Roland_TR-808" - > roland.pdf
```

### Cool stuff:
- Have javascript indicate when the page is ready to print by polling `window.status`
- Specify a cookie (print authenticated pages)

### Options
```bash
usage: docker run -i --rm datasense/wkqt5htmltopdf [-h] [--timeout TIMEOUT] [--window-status WINDOW_STATUS]
                    [--cookie COOKIE] [--js-delay JS_DELAY]
                    URL OUTPUT

positional arguments:
  URL
  OUTPUT                Output pdf file, or '-' for stdout

optional arguments:
  -h, --help            show this help message and exit
  --timeout TIMEOUT     Description for foo argument
  --window-status WINDOW_STATUS
                        Print only when 'window.status' matches this value
  --cookie COOKIE       Use this cookie (must be Base64)
  --js-delay JS_DELAY   Wait this number of seconds before printing

```