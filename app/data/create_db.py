import sqlite3
db_connection = sqlite3.connect("test.sqlite")
cursor = db_connection.cursor()

### Volunteer + Service
# NOTE: Service table has not been created yet
cursor.execute(
    """
    CREATE TABLE ProvidedService (
        id INTEGER,
        service_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(service_id) REFERENCES Service(id),  // TODO: not implem. yet
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
        FOREIGN KEY(address_id) REFERENCES Address(id), // TODO: not implem. yet
        FOREIGN KEY(type_id) REFERENCES VolunteerType(id),
        FOREIGN KEY(visibility_id) REFERENCES Visibility(id), 
        FOREIGN KEY(preferred_contact_method_id) REFERENCES PreferredContactMethod(id), // TODO: not implem. yet

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

#TODO: does not work yet (Staff table dne)
cursor.execute(
    """
    CREATE TABLE RequestVolunteerRecord (
        id INTEGER,
        request_id INTEGER NOT NULL,
        volunteer_id INTEGER NOT NULL,
        status_id INTEGER NOT NULL,
        staff_member_id INTEGER NOT NULL,
        updated_datetime DATETIME NOT NULL,
        PRIMARY KEY(id),
        FOREIGN KEY(volunteer_id) REFERENCES Volunteer(id),
        FOREIGN KEY(status_id) REFERENCES RequestVolunteerStatus(id),
        FOREIGN KEY(request_id) REFERENCES Staff(id) // TODO: not implem. yet
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

db_conn.commit()
db_conn.close()