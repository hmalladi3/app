DATABASE
- accounts table
- services table
- reviews table
- media folder

FEATURES TODO
- add hashtags feature (matrix of hashtags and accounts as db table)
- verify acct
- flag user
- recurring payments

NOTES
- persistent media storage
- non persistent everything else
- password and location is stored in plaintext
- api calls directly from frontend to database, no intermediary

-> HASHTAGS
- list of hashtags for each account
- list of accounts for each hashtag
- this creates a bipartite graph of hashtags and accounts in array list format (do something with this)
- "this can be used for recommendation systems and filtering" - claude 3.5