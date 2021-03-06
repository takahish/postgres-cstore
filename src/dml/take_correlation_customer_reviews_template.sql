-- Do we have a correlation between a book's title's length and its review ratings?
SELECT
    width_bucket(length(product_title), 1, 50, 5) title_length_bucket
    ,round(avg(review_rating), 2) AS review_average
    ,count(*)
FROM
   test.customer_reviews
WHERE
    product_group = '{product_group}'
GROUP BY
    title_length_bucket
ORDER BY
    title_length_bucket
;