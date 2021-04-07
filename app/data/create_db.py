import sqlite3
db_connection = sqlite3.connect("llh-dev.sqlite")
cursor = db_connection.cursor()

### General
cursor.execute(
    """
    CREATE TABLE Address (
        id INTEGER,
        name TEXT NOT NULL,
        street_address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

### Volunteer + Service
cursor.execute(
    """
    CREATE TABLE ProvidedService (
        id INTEGER,
        service_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(service_id) REFERENCES Service(id),  
        FOREIGN KEY(volunteer_id) REFERENCES Volunteer(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE Volunteer (
        id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        birthdate DATE NOT NULL,
        preferred_name TEXT NOT NULL,
        address_id INTEGER NOT NULL,
        phone_number TEXT NOT NULL,
        email_address TEXT NOT NULL,
        company TEXT NOT NULL,
        job_title TEXT NOT NULL,
        type_id INTEGER NOT NULL,
        visibility_id INTEGER NOT NULL,
        last_service_date DATE NOT NULL,
        rating INTEGER NOT NULL,
        is_fully_vetted BOOLEAN NOT NULL,
        preferred_contact_method_id INTEGER NOT NULL,
        general_notes TEXT NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(address_id) REFERENCES Address(id),
        FOREIGN KEY(type_id) REFERENCES VolunteerType(id),
        FOREIGN KEY(visibility_id) REFERENCES Visibility(id), 
        FOREIGN KEY(preferred_contact_method_id) REFERENCES ContactMethod(id) 
    );
    """
)

cursor.execute(
    """
    CREATE TABLE VolunteerType (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE Visibility (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE ContactMethod (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

### Volunteer + Request

cursor.execute(
    """
    CREATE TABLE RequestVolunteerRecord (
        id INTEGER,
        request_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        status_id INTEGER NOT NULL,
        staffer_id INTEGER NOT NULL,
        updated_datetime DATETIME NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(request_id) REFERENCES Request(id),
        FOREIGN KEY(volunteer_id) REFERENCES Volunteer(id),
        FOREIGN KEY(status_id) REFERENCES RequestVolunteerStatus(id),
        FOREIGN KEY(staffer_id) REFERENCES Staffer(id) 
    );
    """
)

cursor.execute(
    """
    CREATE TABLE RequestVolunteerStatus (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)


### Volunteer Availability
cursor.execute(
    """
    CREATE TABLE AvailabilityStatus (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE TimePeriod (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE VolunteerAvailability (
        id INTEGER,
        volunteer_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        time_period_id INTEGER NOT NULL,
        availability_status_id INTEGER NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(volunteer_id) REFERENCES Volunteer(id),
        FOREIGN KEY(time_period_id) REFERENCES TimePeriod(id),
        FOREIGN KEY(availability_status_id) REFERENCES AvailabilityStatus(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE VolunteerVacationDay (
        id INTEGER,
        volunteer_id INTEGER NOT NULL,
        date DATE NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(volunteer_id) REFERENCES Volunteer(id)
    );
    """
)

### Member
cursor.execute(
    """
    CREATE TABLE Member (
        id INTEGER,
        member_number INTEGER NOT NULL,
        salutation TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_initial TEXT NOT NULL,
        last_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        birthdate DATE NOT NULL,
        preferred_name TEXT NOT NULL,
        address_id INTEGER NOT NULL,
        phone_number TEXT NOT NULL,
        email_address TEXT NOT NULL,
        membership_expiration_date DATE NOT NULL,
        volunteer_notes TEXT NOT NULL,
        staffer_notes TEXT NOT NULL,
    
        PRIMARY KEY(id),
        FOREIGN KEY(address_id) REFERENCES Address(id)
    );
    """
)
# TODO: change to ContactLogPriorityType .. no 's'
cursor.execute(
    """
    CREATE TABLE ContactLogPriorityTypes ( 
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE Request (
        id INTEGER,
        type_id INTEGER NOT NULL,
        status_id INTEGER NOT NULL,

        created_date DATE NOT NULL, 
        requested_date DATE NOT NULL,

        initial_pickup_time TIME NOT NULL,
        appointment_time TIME NOT NULL,
        return_pickup_time TIME NOT NULL,
        drop_off_time TIME NOT NULL,

        is_date_time_flexible BOOLEAN NOT NULL,
        short_description TEXT NOT NULL,
        
        service_category_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,

        starting_address_id INTEGER NOT NULL,
        destination_address_id INTEGER NOT NULL,

        duration_type_id INTEGER NOT NULL,
        modified_date DATE NOT NULL,
        requesting_member_id INTEGER NOT NULL,
        special_instructions TEXT NOT NULL,
        followup_date DATE NOT NULL,
        responsible_staffer_id INTEGER NOT NULL,
        contact_log_priority_id INTEGER NOT NULL,
        cc_email TEXT NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(type_id) REFERENCES RequestType(id),
        FOREIGN KEY(status_id) REFERENCES RequestStatus(id),
        FOREIGN KEY(service_category_id) REFERENCES ServiceCategory(id),
        FOREIGN KEY(service_id) REFERENCES Service(id),
        FOREIGN KEY(starting_address_id) REFERENCES Address(id),
        FOREIGN KEY(destination_address_id) REFERENCES Address(id),
        FOREIGN KEY(duration_type_id) REFERENCES DurationType(id),
        FOREIGN KEY(requesting_member_id) REFERENCES Member(id),
        FOREIGN KEY(responsible_staffer_id) REFERENCES Staffer(id), 
        FOREIGN KEY(contact_log_priority_id) REFERENCES ContactLogPriorityTypes(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE RequestDurationType (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE RequestStatus (
        id INTEGER,
        name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE RequestType (
        id INTEGER,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE Service (
        id INTEGER,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(category_id) REFERENCES ServiceCategory(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE ServiceCategory (
        id INTEGER,
        name TEXT NOT NULL,
        is_visible BOOLEAN NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE Staffer (
        id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        PRIMARY KEY(id)
    );
    """
)

db_connection.commit()
db_connection.close()