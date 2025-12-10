Initially we are going to focus on a simple demo and then later think about adding integrations in this order: Speech (Voiced Transcripts) , Power BI , Event hubs

Demo:

 Part 1
  2 modes for input preprocessing: 
  A) Kalsh API data + News API data
  B) Kalshi API data + X , formerly twitter data
  [We may or may not combine this later but for simplicity we'll keep it seperate initally.]

  after this step we either compose this combined data as a unified pdf/doc/csv or perhaps two seperate docs for kalshi and X data that reference a similar topic. (Like who is favored to win the next election)

Part 2

 Here we will perform our AI operations on the data composed from part 1.
 Use Semantic analysis and key phrase extraction to get the data of the general direction of people's opinions
 
 Use the Grok endpoint to interpret the opinion data and how it measures up against the event prediction data from kalshi.
 This will aim to improve and substantiate prediction of future events with actual statistical data.
 
