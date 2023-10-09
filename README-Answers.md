Question 1: Why is performance degrading as the test run longer?

A: After analyze the code more carefully I notice that in get order and create order methods was calling all the products for each element in order_details list, which were making the algorithms lazy with time.

Question 2: How do you fix it?
A: In the create order I just call all the products once and then iterate the list seeking for the ID's inside the order_details list.
And in the get order detail I just remove the unnecessary call listing all products that weren't using anywhere.