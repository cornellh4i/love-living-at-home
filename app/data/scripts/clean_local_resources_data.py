def import_phone_df():
    # Read in all the phone numbers
    phone_df = pd.read_csv('../out/phone_numbers.csv')
    phone_df.columns
    phone_df.drop(columns=['Unnamed: 0', 'Phone ID'], inplace=True)
    return phone_df


def clean_local_resources_data():
    local_resources_df = pd.read_csv('../out/archive/local_resources.csv')
    local_resources_df.rename(columns={local_resources_df.columns[0]: "ID"},
                              inplace=True)

    # replace phone IDs with actual phone numbers
    phone_df = import_phone_df()
    local_resources_df['Primary Phone Number Text'] = [
        phone_df.iloc[int(phone_id)]['Phone Number']
        if not math.isnan(phone_id) else None
        for phone_id in local_resources_df['Primary Phone Number']
    ]
    local_resources_df['Secondary Phone Number Text'] = [
        phone_df.iloc[int(phone_id)]['Phone Number']
        if not math.isnan(phone_id) else None
        for phone_id in local_resources_df['Secondary Phone Number']
    ]
    local_resources_df.drop(
        columns=['Primary Phone Number', 'Secondary Phone Number'],
        inplace=True)
    local_resources_df.rename(columns={
        'Primary Phone Number Text':
        'Primary Phone Number',
        'Secondary Phone Number Text':
        'Secondary Phone Number'
    },
                              inplace=True)

    # Check that all the emergency contact phone numbers are `NaN` in this table, since we'll be removing the column.
    assert (set([
        math.isnan(value) for value in
        local_resources_df['Emergency Contact Phone Number'].values
    ]) == {True})
    local_resources_df.drop(columns=['Emergency Contact Phone Number'],
                            inplace=True)

    # Let's drop the "Notes" column for now and then fill them in later when creating reviews.
    local_resources_df.drop(columns=['Notes'], inplace=True)

    # Rename the columns to match the headers
    local_resources_df.rename(columns={
        'ID':
        'id',
        'Contact First Name':
        'contact_first_name',
        'Contact Last Name':
        'contact_last_name',
        'Company':
        'company_name',
        'Email':
        'email_address',
        'Preferred Contact Method':
        'preferred_contact_method',
        'Website':
        'website',
        'Address ID':
        'address_id',
        'Primary Phone Number':
        'primary_phone_number',
        'Secondary Phone Number':
        'secondary_phone_number'
    },
                              inplace=True)

    # Add randomized availability IDs
    import random
    num_rows = local_resources_df['id'].count()
    local_resources_df['availability_id'] = [
        random.randint(0, 10) for i in range(num_rows)
    ]

    # Print out one of the dictionaries
    print("\nPrinting out one of the data entries as a dictionary")
    for row in local_resources_df.iterrows():
        print(dict(row[1]))
        break

    # Write the table out to a CSV file
    out_csv_name = '../out/local_resources.csv'
    local_resources_df.to_csv(out_csv_name, index=False)
    print(f"\nWrote the data successfully to {out_csv_name}")


if __name__ == '__main__':
    import pandas as pd
    import math
    clean_local_resources_data()
