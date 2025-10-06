import pandas as pd

# How to download the bank transaction report:
# 1) Download csv seperated file from desired start to end date from Rabobank
# 2) Open in Excel and use function 'text to columns'
# 3) Remove all columns except for 'Date' and 'Amount'
# 4) Save as tab delimited .txt file

# How to download the EBH report:
# 1) Go to grootboek current bankaccount
# 2) Select desired date range & start
# 3) Download .csv

# E-boekhouden data
EBH = input("Enter e-boekhouden file name: ")
BANK = input("Enter bank file name: ")
CONVERT_FILE = True

START_DATE = input("Enter start date (DD-MM-YYYY): ")
END_DATE = input("Enter end date (DD-MM-YYYY): ")

# --- Remove unnecessary lines from the E-Boekhouden export ---
if CONVERT_FILE:
    lines_to_delete = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]

    # Read all lines
    with open(EBH, 'r') as f:
        lines = f.readlines()

    # Filter lines by keeping only those not in the list
    filtered_lines = [line for i, line in enumerate(lines) if i not in lines_to_delete]

    # Write the filtered lines back
    with open(EBH, 'w') as f:
        f.writelines(filtered_lines)

# --- Read the CSV files, clean them and convert them ---
df_EBH = pd.read_csv(EBH, sep='\t')
df_EBH.drop(columns=['Kostenplaats'], inplace=True)
df_EBH['Datum'] = pd.to_datetime(df_EBH['Datum'], dayfirst=True)

# Remove points
df_EBH['Activa'] = df_EBH['Activa'].str.replace('.', '', regex=False)
df_EBH['Passiva'] = df_EBH['Passiva'].str.replace('.', '', regex=False)

# Convert numbers to floats
df_EBH['Activa'] = df_EBH['Activa'].str.replace(',', '.', regex=False).astype(float)
df_EBH['Passiva'] = df_EBH['Passiva'].str.replace(',', '.', regex=False).astype(float)

# Convert passiva to minus numbers and merge passiva and activa to one column called 'Amount'
df_EBH['Passiva'] = df_EBH['Passiva'].apply(lambda x: -abs(x) if pd.notna(x) else x)
df_EBH['Amount'] = df_EBH['Passiva'].fillna(df_EBH['Activa'])
df_EBH.drop(columns=['Activa', 'Passiva', 'Nr', 'Omschrijving', 'Relatie', 'Factuur', 'Boekstuk'], inplace=True)

df_BANK = pd.read_csv(BANK, sep='\t')
df_BANK['Date'] = pd.to_datetime(df_BANK['Date'], dayfirst=True)
df_BANK['Amount'] = df_BANK['Amount'].str.replace('.', '', regex=False)
df_BANK['Amount'] = df_BANK['Amount'].str.replace(',', '.', regex=False).astype(float)

# --- Start subsetting data based on begin and end date ---
# Select subset of data based on start and end-date
start_date = pd.to_datetime(START_DATE, dayfirst=True)
end_date = pd.to_datetime(END_DATE, dayfirst=True)

df_EBH_subset = df_EBH[(df_EBH['Datum'] >= start_date) & (df_EBH['Datum'] <= end_date)]
df_BANK_subset = df_BANK[(df_BANK['Date'] >= start_date) & (df_BANK['Date'] <= end_date)]

pairs_EBH = set(df_EBH_subset.apply(tuple, axis=1))
pairs_BANK = set(df_BANK_subset.apply(tuple, axis=1))

# --- Compare the data ---
not_BANK = pairs_EBH - pairs_BANK  # Items in E-Boekhouden not found in the bank
not_EBH = pairs_BANK - pairs_EBH  # Items in the bank which are not found in E-Boekhouden

df_not_BANK = pd.DataFrame(list(not_BANK), columns=['Date', 'Amount'])
df_not_EBH = pd.DataFrame(list(not_EBH), columns=['Date', 'Amount'])

df_total = pd.concat([df_not_BANK, df_not_EBH], axis=1)
df_total.columns = ['Not in bank', 'Amount EBH', 'Not in EBH', 'Amount bank']

# --- Present and export data
df_total = df_total.to_csv('Faults in the current bankaccount.csv', index=False)
# df_not_BANK.to_csv('Not found in bank.csv', index=False)
# df_not_EBH.to_csv('Not found in E-boekhouden.csv', index=False)

print(f'Total mismatches EBH = {len(df_not_EBH)}')
print(f'Total mismatches bank = {len(df_not_BANK)}')
