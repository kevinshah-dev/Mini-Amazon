\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Categories FROM 'Categories.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.products_id_seq',
--                          (SELECT MAX(id)+1 FROM Products),
--                          false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.products_id_seq',
--                          (SELECT MAX(id)+1 FROM Products),
--                          false);

\COPY AddedProducts FROM 'AddedProducts.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.products_id_seq',
--                          (SELECT MAX(id)+1 FROM Products),
--                          false);

\COPY Supply FROM 'Supply.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.supply_id_seq',
--                          (SELECT MAX(id)+1 FROM Supply),
--                          false);
                         
\COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.productreviews_id_seq',
--                          (SELECT MAX(id)+1 FROM ProductReviews),
--                          false);

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.carts_id_seq',
--                          (SELECT MAX(id)+1 FROM Wishes),
--                          false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY SellerReviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV