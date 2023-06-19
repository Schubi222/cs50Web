# Distinctiveness and Complexity
### Distinctiveness
This project distinguishes itself from the other assignments as its purpose is a completely different. Instead of it being a platform for users to just share something with other users it provides the opportunity for users to share their problems with the support team of for instance a company which than in return can claim the tickets and work to find a solution for the problem. Furthermore, the team system provides the support team with the opportunity to group specialised workers of the same expertise together and therefore allow for a better workflow. While doing so the user can see the whole log of notifications and comments made to their tickets which might imply progress or further questions about their problems. It also distinguishes itself from the other assignments by having a permission system which grants different access rights for different roles. 
### Complexity
The ticket system takes the complexity of the former assignments like creating the listings in the second assignment or the posts in the fourth assignment which is also present in this project in the form of the tickets and clearly adds to it. It does so by adding more actions as in claiming, and assigning tickets as well as the whole team dynamic and the different roles for the user which come with different permissions which also implies additional filter while also being dynamic and reloading only the things that have changed rather than reloading the whole page. A further increase in complexity are the notification pop-ups which display the success or failure of different actions. The dashboard is as mentioned a library provided by google but its use still is an additional feature compared to the other assignments and therefore adds to the complexity.
As for the complexity of the models it might slightly exceed the complexity of the fourth assignment but not in a significant way, I would therefore argue that it is as complex.
# Description of each file
The css/js/html files that have the same name always belong together. Furthermore index.html, allTickets.js and ticket.css belong together. The combination of these files makes up the functionality of the given page. The HTML will mostly just provide a few container divs and extend the layout and the related css files will provide the style. Furthermore, everywhere it is not explicitly mentioned only open tickets are displayed as well as only tickets the user has permission to see are shown. If this is the case, I will not mention it throughout this listing

For archive the js file simply loads the archive which contains all closed tickets and in case there are no tickets it displays so and otherwise it displays all the tickets and the pagination. 

For the dashboard the js file gets the data for the three different charts. The first displaying the stats for the user, the second for the team and the third for the whole system. Should any of them have no tickets it will display the highest level (user < team < system). After getting the data it will draw the chart as described in the documentation (https://developers.google.com/chart)

The index.html in addtion contains a form for creating a new ticket. The associated “allTickets.js” loads all tickets the user has permission to see and in case there are no tickets it displays so and otherwise it displays all the tickets and the pagination. Additionally, it provides the functionality for creating a new ticket.

The layout.html contains the whole menu bar as well as some variables which are passed as json objects to all the JS files. The related js file creates the functionality for the “hamburger” for opening the menu as well as making sure that once a message is displayed it first of al gets shown and after some time hidden again as well as make sure that it will still be displayed if for instance the ticket is opened after claiming the ticket. 

The login and register htmls are taken from the previous assignments and slightly adapted but the functionality stays the same. 

For the myteam Html it implements the form for creating a new worker and a new team which are hidden in the beginning. The JS file implementation the functionality for creating a new worker and team as well as loading the team of the given worker and the tickets which are associated with the team of the worker. 

The js file for myticket loads the tickets that have been created by the user and in case they are a worker also the tickets that have been assigned to the worker. 

The profile html displays some basic infos about the user of the profile.  The JS dose the same as for myticket but for the user of the profile and adds a bit more info. 

The ticket html displays the information about the ticket. Furthermore, it displays a message if the ticket has been closed and provides some buttons in case the user has the permission to make these actions. Additionally, it also creates a form which allows users and workers to leave a comment. The JS file creates the functionality for commenting, claiming, reassigning and closing the ticket as well as loading the log of notifications and comments. 
### Further JS and CSS files
Container.css contains the style for listed tickets, comments and notifications.

Form.css contains the style for the forms (some specific styling may be found in the page specific css files)

Noselect.css contains a class that prevents everything that has the given class from being selected. 

Util.js contains generic functions that might be need multiple times with slightly different parameters like comment vs notifications vs tickets. 
# How to run the application
Make sure that all migrations have been made. 

Create a superuser.

Run the application.

Go to the website. Go to /admin and change the “Permission” field of the superuser to “Lead_Worker” (this has only to be done for the superuser as there is no custom superuser)

From there on everything is accessible and the lead worker can create new lead workers as well as normal workers. 

Additionally, in order to see the dashboards internet connection is required.
# Additional Information
Register.html, Login.html as well as the views register, login_view and logout_view have been taken from the previous assignments and slightly adapted. Furthermore, the dashboard is provided by google (https://developers.google.com/chart) and requires internet connection.
