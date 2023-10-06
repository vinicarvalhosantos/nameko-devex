Question 1: Why is performance degrading as the test run longer?

A: In my case performance was degrading because it was not calling the DELETE methods at the end of the tests, which makes the average response time grow to 529ms and 90% response time to 1.46 seconds as we can see in the test: https://a.blazemeter.com/app/?public-token=1KQRclU93Tf5q3EVSMHbl54Y4NlZivvI05s4s2VQxO82QNcFQm#/accounts/-1/workspaces/-1/projects/-1/sessions/r-ext-65200d2da6424992755253/summary/summary
When I use the DELETE methods the average response time down to 10ms and 90% response time to 19ms as we can see in the test: https://a.blazemeter.com/app/?public-token=3wto2IUbcBq2nBH38B490lC22Fngi189YevFFKjkQduPVR8fAi#/accounts/-1/workspaces/-1/projects/-1/sessions/r-ext-65200b828b225232606385/summary/summary

Question 2: How do you fix it?
A: At the of each flow, I created a test to call the order and product DELETE endpoint decreasing the average response time abruptly.