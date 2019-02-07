import json
import os

output_dir = './output'
with open('./record.json',"r") as f:
    crawler_status = json.load(f)

crawler_status_clean = dict()
most_outlink_all = 0
most_outlink_valid = 0
most_outlink_all_url = []
most_outlink_valid_url = []

for key in  crawler_status:
    if not crawler_status[key]['visited']:
        continue
    crawler_status_clean[key] = crawler_status[key]
    if len(crawler_status[key]['children']) >  most_outlink_valid:
        most_outlink_valid_url = [key]
        most_outlink_valid = len(crawler_status[key]['children'])
    elif len(crawler_status[key]['children']) ==  most_outlink_valid:
        most_outlink_valid_url.append(key)
    if len(crawler_status[key]['children'])+ len(crawler_status[key]['invalid']) >  most_outlink_all:
        most_outlink_all_url = [key]
        most_outlink_all = len(crawler_status[key]['children'])+ len(crawler_status[key]['invalid'])
    elif len(crawler_status[key]['children'])+ len(crawler_status[key]['invalid']) ==  most_outlink_all:
        most_outlink_all_url.append(key)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(os.path.join(output_dir,'result.json'),"w") as f:
    json.dump(crawler_status_clean,f)
with open(os.path.join(output_dir,'result.txt'),"w") as f:
    f.write("Most outlink url(including invald):"+ ','.join(most_outlink_all_url)+"; have "+str(most_outlink_all)+" outlinks.\n")
    f.write("Most outlink url(only valid):"+ ','.join(most_outlink_valid_url)+"; have "+str(most_outlink_valid)+" outlinks.\n")

