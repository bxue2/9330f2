# Import Prospects from a CSV File - Backend Implementation

<!-- Please fill out commented out fields -->

## Discuss Alternatives

<!-- What are some alternative approaches we can take when implementing this feature? -->
1. I chose to parse the CSV server-side, but you could parse the CSV on the client-side, instead of uploading it to the backend and parsing it there. So step 1 would not actually do anything with the file until after the Import button on step 2 is pressed.

2. For step 3, using something like Server-Side events might make more sense than using a REST API to get the upload status.

<!-- Please analyze each alternatives and discuss pros/cons here. -->
### Analysis
1. This approach simplifies a few things. We don't need to upload the whole CSV file for one. We could combine steps 1 and 2; we don't need the first API route, and the 2nd API route could send the already parsed CSV data to the backend to add the DB. The downside is that since all this parsing is done client-side, it puts more strain on the client, might lead to client-side errors, and makes doing things asynchronously difficult (which might be necessary if the file is large enough).
For example, if parsed client-side, there would be problems if the import process was started but the user closed the browser while still parsing. If parsed server-side, as long as the initial file upload went through, the db insertions can happen asynchronously even after the user closes the browser.

2. Using SSE would let the server send the client updates on when things get imported. If we use REST API to get the upload status, the client would have to constantly ping the server to get the update status. Depending how often the average client checks for updates, SSE might update more often, which could mean more network traffic, but it might be more intuitive to have something that changes in real-time rather than only when the user refreshes.

## API Routes

We need to implement 3 API routes in total.

<!-- Route Specification Example
- HTTP Method: POST
- Path: /api/login
- Request Type: { email: string, password: string }
- Response Type: { user: User, token: string }
- Description: Authenticate user by email and password then return a JWT if successful.
-->

1. A Route for uploading CSV
   - HTTP Method: POST <!-- Since we're adding something to the backend -->
   - Path: /api/prospects/uploadcsv
   - Request Type: {file: binary}
      - Use header Content-Type: text/csv
   - Response Type: { success: boolean, error: string }
   - Description: Uploads/Sends the csv file to the backend, returns whether upload was successful or an error.

2. A Route for starting the process of adding prospects to the database
   - HTTP Method: POST
   - Path: /api/prospects/import
   - Request Type: {first_name: int, last_name: int, email: int, overwrite: boolean, ignore_header: boolean}
      - int refers to the corresponding column number in the csv
      - overwrite/ignore_header refer to the options I see in the screenshot
   - Response Type: {success: boolean, error: string, upload_id: int}
   - Description: When the user confirms the matching columns, this API posts the parameters so backend knows how to process the CSV, and returns success/failure status, plus an id number for the upload batch (for tracking purposes).

3. A Route for tracking the progress in database insertion
   - HTTP Method: GET <!-- Since we're retrieving info -->
   - Path: /api/prospects/progress/{upload_id}
      - upload_id parameter so we can get the progress of a specific upload batch
   - Request Type: None, since it's a get request
   - Response Type: {count: int, complete: boolean}
   - Description: Returns the number of successful insertions, plus a status report if all insertions are complete.

## Database Changes

<!-- What changes do we need to make in database for this feature? -->
First and last name are not optional in the current database, but they're optional in the requirements, so those columns need to be changed to nullable=True.

You could optionally add a column to prospects to track which upload a row might belong to. Ex. have an upload_id column, so when we track progress, we can query for all rows containing that upload_id. I feel like this could be handled by the server without touching the DB though.

## Additional Changes

<!-- What do we need to implement other than route handlers & database? -->
- Error handling might be a concern, since there's no guarantee the whole CSV will match the required format. Either ignore invalid rows, or just reject the entire import and ask the user to fix the file first. Might need some error handling on the frontend as well (ex. make it clear that email column is required)

- Since we don't upload the file and process it in the same API call, we will need some place to store the CSV file until the 2nd POST request comes in. Probably not in the DB, but in a cache layer (since we don't need to permanently store the CSV file either, probably use LRU algo). Just make sure the cache is large enough so a file doesn't get kicked from the cache before the 2nd POST API call comes in.

- Not sure if I'm expected to go in-depth about this, but scalability might complicate things, especially if we're doing async. For example, there might be problems if a user can upload multiple csv's simultaneously, and there's overlap between the files. If there's multiple databases/servers, you would need to keep them synced as well.

- The screenshot shows an option to overwrite existing prospects. So you'll need some logic to handle finding matching prospects and overwriting them (probably just check for rows with both matching user_id and email).
