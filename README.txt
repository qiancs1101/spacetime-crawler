1. record.json is the raw record that contains both visited and unvisited url. its structure is :
    url:{
        'parent': parent_url,  // which url links to the current url
        'visited': T/F,  // F is still in frontier
        'processed': 0,  // how many children being processed
        'children': [],
        'invalid': []
    }

2. process_record.py is used to process record.json. After processing, two files will be exported in output dir. 
Result.json is the file that contains only visited url. Txt contains most-outlink counts.