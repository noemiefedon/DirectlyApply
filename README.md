# code-test-python

DirectlyApply helps thousands of job seekers apply to jobs across the US everyday. Our platform generates event data for many user events, one of which is an apply event which occurs when a user clicks the "Apply now" button on a job listing and begins the application process.

See the enclosed sample apply event data for one of our clients DoorDash.

#### The data contains the following fields:
 - id (unique id for the event)
 - created (What time (UTC) the event took place)
 - eventType (The type of event on the DirectlyApply platform)
 - eventValue (The value of the event (USD) in cents)
 - jobId (unique id for the job listing the event occurred on)
 - country (country of the job)
 - slug (company name)
 - geo (longitude, latitude)
 
#### Your Task
1. Use the below API endpoint to add US State data to each event row
2. Create a visualisation showing distribution of events across states (e.g. bar charts, maps)
3. Create a visualisation showing the sum value of events across states
4. Identify and visualise temporal trends of the event data (e.g. moving average of total daily eventValues)

#### State API
https://us-state-api.herokuapp.com/?lat=36.7&lon=-119.67

If you provide an accurate latitude & longitude the API will return the following response:

```
{
  "state": {
    "name": "California",
    "slug": "california",
    "postal": "CA"
  }
}
```
