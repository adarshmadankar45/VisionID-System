# VisionID-System

Project Description:
This Criminal Database Management System is a comprehensive web application designed for law enforcement agencies to efficiently manage criminal records. The system provides secure admin access, criminal record creation, advanced search capabilities, and facial image matching functionality.

Key Features:
1. Secure Admin Authentication
•	Role-based access control system
•	Encrypted password protection
•	Session management
2. Criminal Record Management
•	Add new criminal records with detailed information:
    	First name, last name, and optional middle name
    	Date of birth (with auto-calculated age)
    	Gender selection
    	Multiple image upload capability
•	Edit existing records	
•	Comprehensive data validation
3. Advanced Search Functionality
•	Name-based search for quick record retrieval
•	Image-based search using facial recognition:
    	Upload multiple photos to find matching criminal records
    	Supports JPEG and PNG formats
    	Displays matching probability scores
4. Dashboard Interface
•	Real-time criminal database statistics
•	Quick access to all system functions
•	Date and time display

Technology Stack:
•	Backend: Python with Django framework
•	Frontend:
    	HTML5, CSS3
    	JavaScript for interactive elements
    	Bootstrap for responsive design
•	Database: MySQL/SQLite (configurable)
•	Additional Libraries:
    	Django authentication for secure login
    	Image processing libraries for facial recognition
    	Date/time handling utilities
    
Usage Guide:
•	Admin Login
  	Access the login page at /admin
  	Enter credentials created during superuser setup
  	Navigate through the dashboard using the sidebar menu
•	Adding Criminal Records
  	Click "Add Criminal" from the dashboard
  	Fill in all required fields (marked with *)
  	Upload one or more images of the criminal
  	Click "Submit Criminal Record" to save
•	Searching Records
  	Name Search: Enter full or partial name in the search field
  	Image Search: Upload criminal photos to find potential matches
  	View detailed records by clicking on search results
•	Image Management
  	Add additional images to existing records via the image search results
  	Multiple images per criminal are supported for better identification
  
Screenshots:
•	Admin Login Page
![Screenshot 2025-06-29 202402](https://github.com/user-attachments/assets/3de20ba1-ae57-4ebf-af3d-63d9c96a476f)

•	Dashboard View
![dashboard](https://github.com/user-attachments/assets/c80134a4-73c1-4f7c-a468-8a3b4aef69e0)

•	Add Criminal Form
![add](https://github.com/user-attachments/assets/a658c32c-89d8-495c-a870-7671f7058040)

•	Search Interface
![search im](https://github.com/user-attachments/assets/2dc035a9-de41-41e7-a115-f92b8514ec9a)

Future Enhancements
•	Integration with national criminal databases
•	Advanced analytics and reporting features
•	Mobile-responsive design improvements
•	API for third-party system integration
•	Enhanced facial recognition algorithms



