# Take Home Assessment


## Info Candidate:
#### Name: Juan David Hernández Giraldo
#### Email: jdhernandez@azzertai.com
#### Linkedin: https://www.linkedin.com/in/juandhernandez/
#### Github: https://github.com/davoshack
#### Personal site: https://www.davoscode.com/


# Build a python web crawler

Build a simple Python web crawler. Given a starting URL, crawl all links on the website up to a specified depth. 

For this assessment, you are free to use any AI-assisted code generators (Cursor, GitHub Copilot, etc). We recommend not spending more than 1 day on this assignment. This assessment is meant as a starting point for a technical interview.

### Input

- **max-depth**: The maximum depth of links to crawl.
- **domains**: A list of domains to restrict crawling to (if none, crawl all links).
- **blacklist**: A file or list of extensions to ignore during crawling (e.g., `.jpg`, `.css`).

### **Output**

For each crawled URL, the following information should be captured and stored:

- **Status Code**: HTTP status code of the response (e.g., 200, 404).
- **Content Size**: Size of the response content in bytes.
- **Content Title**: The title of the page (from the `<title>` tag in HTML, if available).
- **Statistics**
    - **Total number of URLs crawled**.
    - **Total number of errors** encountered during crawling.
    - **Status code statistics**: Number of crawled URLs per HTTP status (e.g., how many 404s, how many 200s).
    - **Domain statistics**: Number of crawled URLs per domain.
