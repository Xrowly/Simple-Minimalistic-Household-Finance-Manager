# Simple Minimalistic Household Financial/Capital Manager (Version 0.1.0 - Monolithic)

This is a prototype desktop app to help you track your household finances and capital in a simple way. Built with Python and Tkinter, it’s a single-file tool (Version 0.1.0) for managing categories, transactions, and cash. It’s not fancy, just a starting point for home use. Made on October 10, 2025.

## What Is This App?
The **Simple Minimalistic Household Financial/Capital Manager** is a prototype to organize your money into categories (Virtual, Cash, or Summary), add transactions, and check balances. It’s one Python script (`finance.py`) that saves data to a `finance_data.json` file. Think of it as a rough draft for tracking your household budget—basic but functional.

## How to Use It
### Get It Running
1. **What You Need**:
   - Python 3.x (check with `python --version`).
   - No extra libraries—Tkinter’s built-in.

2. **Grab the Code**:
   - Clone it:
     ```bash
     git clone https://github.com/Xrowly/Simple-Minimalistic-Household-Finance-Manager.git
     cd Simple-Minimalistic-Household-Finance-Manager
     ```

3. **Set Up**:
   - Make a `finance_data.json` file in the folder with this (or let it create one):
     ```json
     {
         "children": {},
         "type": "Virtual",
         "balance": 0.0,
         "transactions": []
     }
     ```

4. **Start It**:
   - Run:
     ```bash
     python finance.py
     ```
   - You’ll get a 1000x600 window (can’t resize it—keeps things simple).

### Using the App
- **Left Side (Categories)**: See your categories in a tree. Click one to check details.
- **Top Right (Details)**: Shows transactions or cash breakdown for the selected category.
- **Bottom Right (Actions)**: Use buttons to do stuff.
- **Buttons**:
  - **Add Category**: Pick a name, choose a type (Virtual, Cash, Summary), and decide if it’s a root or subcategory. Hit Add (see below for details).
  - **Rename Category**: Click a category, hit Rename, type new name.
  - **Delete Category**: Select one, confirm to delete it and its subcategories.
  - **Add Transaction**: Pick a Virtual category, enter amount (positive for income, negative for expenses), and add a note. Hit Add (see below for subtraction).
  - **View History**: Use this to see all transactions for a category, especially for Virtual ones where the regular history is bugging out. Fix coming soon!

#### Category Types Explained
- **Virtual**: A regular category for tracking money with transactions. Use this for bank accounts or budgets. Balance updates with each transaction (e.g., +10.50 for income, -5.00 for spending).
- **Cash**: A category for physical money, broken down into denominations (e.g., €500, €0.1 coins). Edit counts to update the balance—great for cash jars or wallets.
- **Summary**: A category that totals balances of its subcategories. No transactions here—just a overview (e.g., a “Total Savings” category with Virtual/Cash kids).

#### Using Add Category
- Click “Add Category” to open the form.
- Enter a name (e.g., “Groceries” or “Savings”).
- Pick a type: Virtual, Cash, or Summary.
- Choose “Root” to make it a top-level category, or “Subcategory” to nest it under a selected category (click a category first).
- Hit “Add” to save it. If the name’s taken under the same parent, it’ll error out.

#### Subtracting with Add Transaction
- Subtraction is done by entering a negative amount in “Add Transaction” (e.g., -10.50 for an expense like a bill).
- Select a Virtual category, type the negative number, add a description (e.g., “Rent”), and click “Add.”
- The balance will decrease accordingly. Positive amounts add to the balance (e.g., +20.00 for a paycheck).

#### Parent-Child Relationships
- **How It Works**: Categories can have subcategories (children) under a parent category. The tree on the left shows this hierarchy. For example, you could have a “Household” parent with “Groceries” and “Utilities” as kids.
- **Adding a Child**: Select a category (the parent), click “Add Category,” choose “Subcategory,” and give it a unique name. It’ll nest under the selected parent.
- **Adding a Root**: Pick “Root” to create a top-level category with no parent—starts at the top of the tree.
- **Balance Impact**: A parent’s balance (if Virtual or Cash) adds to its own transactions, while a Summary parent totals its children’s balances. Deleting a parent removes all its kids too.

- **Saving**: Changes save to `finance_data.json` automatically. Close to quit.

## Limitations
- **Prototype**: One file (`finance.py`, ~600+ lines)—messy to edit, no modules yet.
- **No Help**: No guide inside—learn by doing.
- **Fixed Size**: 1000x600, might look weird on small screens.
- **Local Only**: Data stays in one JSON file—no backups or cloud.
- **Basic Errors**: Crashes on bad JSON—start over if it breaks.
- **Cash Limits**: Denominations are fixed (e.g., €500 to €0.1)—no custom ones.
- **No Export**: Can’t save data outside the JSON yet.
- **Transaction History Bug**: Virtual category history in the Details pane is glitchy—use “View Full History” as a workaround. Fix is in the works!
- **Other bugs may be present 

## Screenshots

![Main Window](screenshots/Screenshot%202025-10-10%20012854.png)
![Transactions](screenshots/Screenshot%202025-10-10%20012905.png)
![Balances](screenshots/Screenshot%202025-10-12%20222114.png)



## Development Notes
- This is a prototype (Version 0.1.0), all in one file. Might split it later.
- Fixed action panel text overlap—check console logs for debug stuff.
- Keep `finance_data.json` private—it’s your data.

## Contributing
Tweak it if you like. Fork it, change stuff, and send a pull request. No strict rules—keep it simple.

## License
MIT License—use it how you want. Add a `LICENSE` file if you feel like it.

## Roadmap
- Maybe break it into smaller files someday.
- Add a way to export data (like CSV).
- Could add a basic help popup if needed.
- Fix the transaction history bug soon.

## Contact
- **GitHub**: [Xrowly](https://github.com/Xrowly)
- Drop an issue or idea there!
