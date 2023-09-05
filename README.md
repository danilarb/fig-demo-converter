# Figured Farm to Demo Templates converter
This is a tool to help convert a Figured farm to a demo farm creator template using Figured's public APIs.

Uses python 3.11

### Before running:

1. Create a `.env` file copying the contents from the `.env.example` file in the same directory as the `.env.example` file.
2. Fill out all fields of the `.env` file.
3. Call the 
4. In your `main.py` file's `main()` function, comment out the `transactions.remove_duplicate_crop_transactions()` **AND** `transactions.remove_duplicate_livestock_transactions()` functions.
5. Run `main.py`.
6. Go through the OAuth2 process.

### Running:

- Run `main.py` with the functions/conversions you'd like.
- If you're using the API you MUST go through the OAuth process in the beginning.
- See how to run the duplication removal below.

#### If you'd like to run `transactions.remove_duplicate_crop_transactions()`:

1. Run the tool once with at least the `accounts.convert()` and `transactions.convert()` functions. These functions generate `.json` files used by `transactions.remove_duplicate_crop_transactions()`.
- OR
1. Add your template's `accounts.json` to the `Accounts` directory and your template's `transactions.json` to the `Transactions` directory.
2. Create your crop season's `invoices.json` invoice file (in the current format as of the _5th of September, 2023_).
3. Copy your `invoices.json` file into this tool's `Transactions` directory, in the same directory as `transactions.py`.
4. Comment out all functions in `main()` other than `transactions.remove_duplicate_crop_transactions()`.
5. Run `main()`.
6. Your transactions (now excluding the crop season's invoices) should be generated in the `new_transactions.json` file.
 
#### If you'd like to run `transactions.remove_duplicate_livestock_transactions()`:

1. Run the tool once with at least the `livestock.convert()` and `transactions.convert()` functions. These functions generate `.json` files used by `transactions.remove_duplicate_livestock_transactions()`.
- OR
1. Add your template's farm's `transactions.json` to the `Transactions` directory.
2. Create your livestock tracker's `transactions.json` transactions file and rename it to `livestock.json`.
3. Copy your `livestock.json` file into this tool's `Transactions` directory, in the same directory as `transactions.py`.
4. Comment out all functions in `main()` other than `transactions.remove_duplicate_livestock_transactions()`.
5. Run `main()`.
6. Your transactions (now excluding the livestock tracker's transactions) should be generated in the `new_transactions.json` file.

#### If you run into any issues contact me through GitHub
