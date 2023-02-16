--=====================================================
--=============== Stored Procedures====================
--=====================================================
--as a customer i can:
--1 customer registeration
create proc customer_register
@fname varchar(50),
@lname varchar(50),
@gender varchar(50),
@zip varchar(50),
@Age int,
@country varchar(50),
@city varchar(50),
@password varchar(50),
@email varchar(50),
@phone varchar(11)
AS
declare @lastcustomerid int
if (exists (select * from customers where email = @email))
begin
select 'this email is already used' as error_massege
end
else
begin
insert into customers(fname, lname, gender, zip_code,age, country,city, password, email)
values(@fname,@lname,@gender, @zip,@age, @country,@city, @password, @email)
set @lastcustomerid = scope_identity()
insert into customer_phone values (@lastcustomerid, @phone)
end

--2 customer login
create proc customer_login
@email varchar(50),
@password varchar(50)
AS
if (exists(select * from customers where password = @password and email = @email))
begin
select 'succeful login' as success_message
end
else
begin 
select ' invalid email or pasword. please, try again' as failed_login

--3 add extra phone
create proc add_phone
@customer_id int, 
@phone varchar(11)
AS
insert into customer_Phone values (@customer_id, @phone)

--4 view all products in our e commerce
create proc view_all_products
AS
select product_id, Product_name, price, category_name, subcategory_name, category_name 
from Products p inner join subcategory s on p.subcategory_ID = s.Subcategory_ID
inner join Category c on s.Category_ID =c.Category_ID

--5 search for products by any of their letters 
create proc search_by_product 
@product_letters varchar(50)
as
select product_id, Product_name, price, category_name, subcategory_name
from Products p inner join subcategory s on p.subcategory_ID = s.Subcategory_ID
inner join Category c on s.Category_ID =c.Category_ID
where product_name like '%'+ @product_letters +'%'
--6 adding products to cart
alter proc AddToCart
@product_id varchar(50),
@customer_id varchar(50),
@quantity varchar(50)
AS
declare @i int = 1
while @i <= count(@product_id)
begin
  insert into cart(product_id, customer_id, quantity)
  values(@product_id,@customer_id,@quantity)
  set @i = @i + 1
end 



--7 view products details that is in the cart
create proc view_product_in_my_cart
@customer_id int
as
select product_name, price, quantity, total = price*quantity 
from cart c inner join products p on c.product_id = p.Product_ID
where c.customer_id = @customer_id

--8 viewing price details before make order
alter proc total_price_cart
@customer_id int
as
select cart_subtotal = sum(quantity*price), tax = sum(quantity*price)*0.14, 
freight = 0.07*sum(quantity*price), total = 1.21*sum(quantity*price)
from cart c inner join products p on c.product_id = p.Product_ID 
where customer_id = @customer_id

--9 change quantity of certain products
create proc change_quantity_of_certain_product
@customer_id int,
@product_id int,
@new_quantity int
as
update cart 
set quantity = @new_quantity
where customer_id = @customer_id and product_id = @product_id

change_quantity_of_certain_product 1,1,3

--10 can remove products from cart
create proc remove_product_from_cart
@customer_id int ,
@product_id int
as
delete from cart where customer_id = @customer_id and product_id = @product_id

--11 can empty all of the cart
create proc empty_cart
@customer_id
as
delete from cart where customer_id = @customer_id

--12 can make order from products added to the cart
alter proc MakeOrder 8, 'cash', 'cairo'
@customer_id int,
@payment_method varchar(50),
@shipping_city varchar(50)
AS
declare @order_id int
insert into orders(shipping_city,payment_method,customer_id, order_date)
values(@shipping_city,@payment_method,@customer_id, GETDATE())

set @order_id = SCOPE_IDENTITY()

declare @product_id int, @quantity int

insert into Order_details(quantity,Product_ID,Order_ID)
select quantity,product_id,@order_id from cart where customer_id = @customer_id

delete from cart where customer_id = @customer_id

--13 fill rating survey
alter proc Rating_survey 
@customer_id int,
@overall_rate int,
@delivery_rate int,
@customer_service_rate int,
@loyality varchar(50),
@product_quality_rate int
as
insert into ratings (overall_rate, delivery_rate, customer_service_rate,
product_quality_rate,loyality, customer_id)
values (@overall_rate, @delivery_rate, @customer_service_rate,@product_quality_rate,
@loyality, @customer_id)

--14 can view his order history
alter proc order_history 
@customer_id varchar(50)
as
select * from orders where customer_id = @customer_id

--15 viewing product history
create proc product_history
@customer_id int
as
select product_name, price, quantity, order_date from 
products p inner join order_details od on p.Product_ID = od.product_id
inner join orders o on od.order_id = o.order_id
where o.customer_id = @customer_id
--===========================================================================
--===========================================================================
--==================AS a Business Analyst I Can==============================

--16 view customer rates
create proc customer_rates
as
select avg(overall_rate) as over_all_rate, avg(delivery_rate) as deliver_rate
, avg(product_quality_rate) as product_quality_rate,
avg(customer_service_rate) as customer_service_rate
from ratings

--17 view what rates affecting loyality
create proc customer_rates_based_on_loyality 
as
select loyality, avg(overall_rate) as over_all_rate, avg(delivery_rate) as deliver_rate
, avg(product_quality_rate) as product_quality_rate,
avg(customer_service_rate) as customer_service_rate
from ratings
group by loyality

--18 view overall sales details
create proc overall_total_sales
as
select total_sales = sum(total_due),total_taxes = sum(total_tax), 
total_freight = sum(total_freight) , total_subtotal = sum(sub_total) 
from orders

--19 view sale by entering city letters
create proc sales_per_city 
@city varchar(50)
as
select shipping_city, sum(total_due) as total_sales
from orders 
group by shipping_city having shipping_city like '%'+@city+'%'

--20 view sales based on gender
create proc sales_per_gender
as
select gender , sum(total_due) 
from orders o inner join customers c on o.customer_id=c.customer_id 
group by gender

--21 view sales for every age category
create proc get_sales_by_age_category
AS
declare @categories table (age_category varchar(50), total_sales int)
insert into @categories (age_category, total_sales)
SELECT 
        CASE
            WHEN age <= 20 THEN 'Under 20'
            WHEN age BETWEEN 21 AND 30 THEN '21-30'
            WHEN age BETWEEN 31 AND 40 THEN '31-40'
            WHEN age BETWEEN 41 AND 50 THEN '41-50'
            WHEN age > 50 THEN 'Over 50'
        END, 
        sum(total_due)
    FROM orders JOIN customers
    ON orders.customer_id = customers.customer_id
    GROUP BY age;
select sum(total_sales), age_category 
from @categories group by age_category

--23view top 10 sales products
create proc top_ten_products
as
select top 10 sum(line_total), product_name from order_details od inner join Products p
on od.product_id = p.Product_ID 
group by Product_name
order by sum(line_total) desc

--23 view lowest sales 10 products
create proc lowest_ten_products
as
select top 10 sum(line_total) as total_sales, product_name from order_details od inner join Products p
on od.product_id = p.Product_ID 
group by Product_name
order by sum(line_total) asc

--24 view pivot table of sales of all products in each month in a given year
create proc products_sales_per_months 
@year int                   
as
select ProductName, 
       ISNULL([1],0) as Jan , 
       ISNULL([2],0) as Feb, 
       ISNULL([3],0) as Mar,
       ISNULL([4],0) as Apr , 
       ISNULL([5],0) as May, 
       ISNULL([6],0) as Jun, 
       ISNULL([7],0) as Jul,
       ISNULL([8],0) as Aug,
       ISNULL([9],0) as Sep,
       ISNULL([10],0) as Oct, 
       ISNULL([11],0) as Nov, 
       ISNULL([12],0) as Dec
 from  ( SELECT MONTH(o.order_date) AS orderDate, p.product_name AS ProductName,
	SUM(isnull(od.line_total,0)) AS LineTotal
    FROM orders o 
    INNER JOIN order_details od ON o.order_id = od.order_id 
    INNER JOIN products p ON od.product_id = p.Product_ID
    WHERE YEAR(o.order_date) = 2022
    GROUP BY MONTH(o.order_date), p.product_name
) as total_product_sales

PIVOT (
SUM (LineTotal)
FOR orderDate IN ([1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12]))
AS pivot_productSales














		







