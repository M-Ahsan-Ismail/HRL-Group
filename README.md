# HRL-Group

## Dealer_Management & Portal

#### Dealer Management
Customized the inventory , added menus for brands , models , variants , fetures , model_types, on product_template form user can check is_vehicel (marking i shows vechile oreinted fields) is_spare_part (marking it shows spare part oriented fields), fields for model details to engine details.
Customized the contact from added , is_dealer , related_dealer (M20 with users) to confirm weather the contact is dealer or customer.
Added separate menus in DMS for viewing dealers , customers.
added menus in DMS for viewing products , spare parts and variants based on filtering recs.
Developed the dealer agrement form includes details from dealer details to brand covers to certificates  to max capital with detailed qweb pdf report.


#### Portal
1: Developed the modern and futuristic design dealership management portal having navbar for scroling between application and status section , enables individuals to apply for a dealership partnership by providing detailed information, including personal details, contact , location , diff certificates and investment capacity. Upon submission, system generates tracking ID for the user to monitor status via portal. portal displays the application state along with relevant details. Adminis can review applications, approve, or reject them. Upon approval, the system automatically creates a partner record for the approved request.

2: Developed the modern dashboard for admin on portal to view specific month (new dealer , approved and pending) applications and all dealers with details like Applicant,	Company,	Business Type and 	Country.
---- Developed the sales dashboard for admin to view speific user , specific duration sales with details like product , sale order , amount , status etc.
---- Developed the opportunity dashboard for admin to view specific users , specific duration leads with some details like Opportunity,	Description,	Expected Revenue and	Stage etc.




## Sales_Warranty & Portal
Developed the Warranty Card Module, that streamlines warranty management. It allows to add warranty duration, on the product form and generate warranty cards for products within sale order lines by clicking the "Add Warranty" button. A wizard opens with pre-filled details, automatically calculating the warranty end date and duration based on the product's form warranty settings. The module first checks if the product is already under an active warranty for the sale order, preventing duplicates. If no active warranty exists, it creates a new warranty with a unique warranty number, linked to the sale order via smart button. On warranty form, users can select terms and conditions, as well as specify what is included and excluded in the warranty, with a dedicated configuration menu to manage these details. 
Implemented cron job for warranties whose end date is coming that suto checks today.date is end date of any warranty and expires that.
Developed the moderan warranty portal where user can track his warranty details.
The module generates a PDF warranty card report displaying product information, warranty details, remaining time, and more. Additionally, a hyperlink redirects users to a modern warranty portal where they can view warranty status, remaining time, and other details by entering their warranty number. 
Added a "Send by Mail" button on the Warranty form. Clicking the button opens the email composer with the Warranty Card PDF automatically attached. When the email is sent, it is delivered to the associated partner's email address.
Admin can force_expire the card also.


## Leave Request Portal
Developed a custom leave request portal with modern UI design using dynamic elements and clean layout.
Enhanced the leave type configuration to clearly define categories such as Hajj/Umrah, Sick, Casual, Annual, Compensatory, and Unpaid.

##### Enabled users to:
View all applied time offs with their current status: Approved, Pending, Rejected, etc.
Apply for new time off by selecting leave type, reason and start/end date or half day or custom hours.
Automatically show/hide the document upload field based on selected leave type (e.g., shows only for "Sick").
Update or cancel time offs if they are still in the To Approve stage.
View all  category allocated leaves , remaining and requested leaves.
Users can filter time offs by last week, last month, last year.
Users can group by leave type or status and sort by start date, end date, or duration and can reset.

##### If a time off request Rejected or Approved:
Rejected: a red banner appears with a rejection message, all fields become read-only, and action buttons are disabled.
Approved: a green banner is shown with approval notice, and all fields/buttons are read-only to prevent edits.



## Attendance History Portal
Users can view their attendance records by providing a date range(Check In , Check Out).
Implemented pagination to show 10 recs/page and for efficient memory use and to reduce server load. 
Can apply quick filters such as Last Week, Last Month, or Last Year.
Attendance report also displayed, including the total number of hours worked of selected period, total days worked, average hours per day, total leaves and the overall attendance status.


## Employee Expense Portal
Developed expense portal , allows users to submit expenses by providing a description, category, date, amount, and payment mode (company or employee).
All submitted expenses are displayed for user review.
Users can update expenses before approved status.
Portal supports filtering expenses by last week, last month, or last year, and grouping expenses by status.




## Loan & Advances Portal
Designed and implemented a comprehensive Loan & Advances Portal that allows users to:
View a complete history of their applied loans
Update or cancel loan requests while in the Draft stage
Submit new loan applications through a user-friendly interface
View detailed installment breakdowns
supports multi compnay.
Efficiently search, filter, group, and sort loan records using advanced tools.


## Grievance Management & Portal

Developed the Grievance Management Module, allowing employees to submit grievances through a modern, user-friendly portal. Employees can select the grievance type, provide issue details, and optionally upload supporting documents. Upon submission, a tracking ID is generated and displayed. The portal features a modern design with a responsive navbar that allows seamless navigation between submission and tracking forms.

Each grievance record automatically captures the employee (based on env.user), their department, submission date, issue description, and any uploaded documents. Administrators can assign HR personnel to handle the grievance, and update its status by resolving, rejecting, or closing the case.









