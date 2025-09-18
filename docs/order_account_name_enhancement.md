# Order Account Name Enhancement

## Overview

This enhancement adds the `account_name` field to order records in the system. Previously, orders only stored the `account_id` which required an additional lookup to display the human-readable account name. With this enhancement, the account name is stored directly with the order data for easier display and querying.

## Implementation Details

### Frontend Changes

In the web interface, when creating an order, the system now captures the selected account's display name and includes it in the order data sent to the backend.

Key changes in `web/templates/stocks.html`:

1. Added code to extract the selected account's display name from the dropdown:
   ```javascript
   const accountSelect = document.getElementById('accountSelect');
   const selectedOption = accountSelect.options[accountSelect.selectedIndex];
   const accountName = selectedOption.textContent;
   ```

2. Included the account name in the order data:
   ```javascript
   const orderData = {
       date: document.getElementById('buyDate').value,
       account_id: document.getElementById('accountSelect').value,
       account_name: accountName,  // Add account name to order data
       code: document.getElementById('stockCode').value,
       name: document.getElementById('stockName').value,
       price: parseFloat(document.getElementById('buyPrice').value),
       quantity: parseInt(document.getElementById('buyQuantity').value)
   };
   ```

### Backend Changes

In the backend API (`web/app.py`), the order creation endpoint was updated to include the `account_name` field in the database record:

```python
# Prepare order document
order = {
    "date": data["date"],
    "account_id": data["account_id"],
    "account_name": data.get("account_name", ""),  # Add account_name field
    "code": data["code"],
    "name": data["name"],
    "price": float(data["price"]),
    "quantity": int(data["quantity"]),
    "total_amount": float(data["price"]) * int(data["quantity"]),
    "created_at": datetime.now()
}
```

The `data.get("account_name", "")` approach ensures backward compatibility by providing an empty string as default if the field is not present in the request.

## Benefits

1. **Improved Performance**: Eliminates the need for additional database lookups to display account names
2. **Better User Experience**: Account names are immediately available in order listings
3. **Simplified Queries**: Account name information can be directly queried without joins
4. **Backward Compatibility**: Existing orders without the field continue to work correctly

## Database Impact

This change adds a new field to the orders collection in MongoDB. Existing records will not have this field, but the system handles this gracefully by showing an empty string when the field is missing.

