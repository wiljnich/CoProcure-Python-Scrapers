# Scraping contracts with python

Identify your scraping target from out <a href="https://docs.google.com/spreadsheets/d/1AHpjv2U8hYpWb1b6BFdXuo6EWS99vrRQicGUpvsB-ds/edit#gid=0">spreadsheet</a> write some code to pull the data from it and create individual records for each individual contract like: <a href="example.json">example.json</a>

The field names in the JSON documents you generate should match the example file. If we discover more information we want to retrieve from new sites make a pull request to this repo to keep the example.json up to date with all the latest field names.

To add code to this repository:
- Work in a new branch you create and when ready open a pull request to master.
- Create a new folder named for each new datasource
- Each new folder should be its own npm package with its own package.json and set of dependencies

The difference between the scrape-v2-python and prior scraping activity we've done in other repositories like scrape-contracts is we are simplifying by separating the initial scraping data retrieval from the additional processing steps(document retrieval and storage, OCR processing, sending final data to cloudsearch and dynamoDB). We can move onto another data source once its data has been saved in this or the scrape-v2-js repository in the expected json format.

## There will be weirdness

Every data source is different and has its own challenges. Most data sources we have encountered so far provide only a small subset of the fields we have seen so far. If we have some type of contract document and a title that is a helpful record. We may encounter situations where it is extremely difficult to write code to extract some of the information from a source. Feel free to discuss that with other folks and make a call on whether we should skip retrieving that part of the data for now. We may be engaging mechanical turkers or offshore data entry teams to backfill some of the fields it is difficult to extract programatically.

### Define a unique id per contract

We need a unique id for each contract. The unique ids are required by the CloudSearch index and we will also use them to allow users to favorite and share links to specific contracts. These links should continue to work if the contract data is rescraped or we augment the contract record with additional data.

If the source provides a contract id and we can separate that easily and we can use that as part of a unique id that is good because it helps us identify the same contract when we encounter it again. If a source presents every contract at their own url we should store the unique url as well, that will probably be helpful unless they change their url structure.
