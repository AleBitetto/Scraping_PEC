# Scraping PEC
Python notebook to scrape PEC from VAT number.

### Installation

Clone the repository with
`git clone https://github.com/AleBitetto/Scraping_PEC.git`

From console navigate the cloned folder and create a new environment with:
```
conda env create -f environment.yml
conda activate scraping_PEC
python -m ipykernel install --user --name scraping_PEC --display-name "Python (Scraping PEC)"
```
This will create a `scraping_PEC` environment and a kernel for Jupyter Notebook called `Python (Scraping PEC)`



### Chrome Web Driver

To download data, this notebook relies on [`selenium`](https://selenium-python.readthedocs.io/) and [`ChromeDriver`](https://chromedriver.chromium.org/).

This requires a `chromedriver` executable which can be downloaded [here](https://chromedriver.chromium.org/downloads). Make sure that your `Chrome` version is the same as your `chromedriver` version.

`scraping_PEC` assumes that the `chromedriver` executable is located at `/WebDriver` in the main folder. To supply a different path, change the variable `chromedriver_path` in the notebook.


### Usage

Simply run the [notebook](https://github.com/AleBitetto/Scraping_PEC/blob/master/Scraping%20PEC.ipynb).

### Notes

Current version works with the Italian language settings and Orbis settings as described in the notebook.
[Katalon Recorder](https://www.katalon.com/resources-center/blog/katalon-automation-recorder/) extension [here](https://chrome.google.com/webstore/detail/katalon-recorder-selenium/ljdobmomdgdljniojadhoplhkpialdid) has been used in order to manually record the steps and convert them into Selenium code.
