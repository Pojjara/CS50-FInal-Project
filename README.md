# J's jewellery store site
#### Video Demo:  https://youtu.be/McrFeYukpEs
#### Description:
Hello, my name is Jacek and for my final project I created a site on which You can purchase jewellery.

Languages/Technologies used:

* HTML
* CSS
* Javascript
* Python
* Flask
* Jinja
* SQLite

## Navigating through the website
To use the site you need be registered and signed in.
Once you do that you're presented with a site which lists all the available products.
On top of the page there's a navbar with which you can navigate to index of the site, open settings in which you're allowed to change your password, open the basket or logout.
Next there's a carousel with all the promotions currently available, since I was creating this website just before Christmass, most of the sales are Christmass oriented.
Through the menu visible udner the carousel you can navigate to all the products you're interested in.
Once you choose a product You can then choose the material the product is made of (Gold or Silver) and the site will only show the ones you want.
Every product has it's own "Card" with price, quantity selector (if a product is a ring there's a size selector visible) and a 'add to basket' button.
On some of the products a discount is applied.
If you click on the item a modal appears with a bigger picture(which can be clicked to open it in another tab with even bigger picture).
Once you add an item to the basket you can then see the basket quantity change in the navbar.
When you open the basket you can see all the items listed, their quantity, unit price, and total price of each item and also a total of all the items in the basket.
You can delete all items together, or each one seperetly.
From basket you can proceed to checkout where you need to give your addres and card information.



## Login()
function checks if the user signs with correct username and password, if not the page is refreshed and flash message appears with corresponding message, for example 'wrong username'.
If the username and password is correct the user id is stored in session so the server remembers which user is logged in.
Logout function works simply, just clears the sessions data.

## Register()
function generetes register.html page.
The registretion form asks for data about username and password.
All users data are stored in sqlite database, every user has unique id, their passwords are hashed with generate_password_hash() function.

## Account()
function helps changing the password if the user wants it.

## add_item_to_basket()
function checks items id and selected quantity that the user wants to add to the basket.
Function checks if the item is already in the basket, if so just increments the quantity, adds the item to the session['basket_item']

## empty_basket()
function clears all the information about the items in the basket but keeps the user logged in, then it redirects the user to the main page.

## delete_product()
function gets the id from the index.html page from basket modal where each item has it's own delete item button, if the button is pressed it sends the id
to the delete_product() function where this item gets deleted, the total price and total quantity updated accordingly to the amount removed.

## checkout()
function just helps checking if the total price to pay is above 100 so it get apply the discount of free delivery

## index()
generates the main page, gives the info about available sizes for rings

## products()
function is the one that gave me the biggest headache
If 'All products' on the main page is clicked the function renders original route which is 'product/'
If the type of the product is selected the function sends sql query to the database that returns only items with selected type
If then the material is also selected it adds to the query the material selected and then renders the page with those items.
