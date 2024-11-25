DATABASE
- accounts table
- services table
- reviews table
- media folder
- hashtags table

FEATURES TODO
- verify acct
- flag user
- payment system
- recurring payments

NOTES
- postgres db
- media folder

-> HASHTAGS
- list of hashtags for each account
- list of accounts for each hashtag
- this creates a bipartite graph of hashtags and accounts in array list format (do something with this)
- "this can be used for recommendation systems and filtering" - claude 3.5

USAGE
- `systemctl start postgresql.service`
- in backend folder: `source bin/activate`
- `PYTHONPATH=$PWD uvicorn src.main:app --reload`