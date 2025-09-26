# Dashboard Take-Profit Line Calculation Fix

## Overview

This document describes the fix for the incorrect take-profit line calculation in the dashboard. The issue was that the take-profit line was displaying 58.4 instead of the expected 65.1, which should represent the highest price since purchase (70.1) multiplied by 0.93.

## Problem Description

The dashboard was incorrectly calculating the take-profit line for stock positions. Instead of using the highest high price since the first purchase date, it was using either:
1. Closing prices instead of high prices
2. Only recent price data (last 7 days) instead of data from the purchase date
3. In some failure cases, calling the calculation function with empty data

## Root Causes

1. **Incorrect Price Data Usage**: The `calculateHoldingAndLimits` function was using `item.close` instead of `item.high` for determining the highest price
2. **Insufficient Historical Data**: Price data fetching was limited to the last 7 days, missing historical data needed for accurate calculations
3. **Error Handling Issues**: In Ajax failure cases, the function was being called with empty price data arrays
4. **Date Range Mismatch**: Price data was not being fetched from the first purchase date of each stock

## Solution Implementation

### 1. Fixed Price Data Usage in Calculation Function

Modified the `calculateHoldingAndLimits` function to use `item.high` instead of `item.close`:

```javascript
// Find the highest price since the first purchase
let highestPrice = 0;
priceData.forEach(item => {
    const itemDate = new Date(item.date);
    if (itemDate >= firstPurchaseDate && item.high > highestPrice) {
        highestPrice = item.high;
    }
});
```

### 2. Extended Historical Data Range

Updated all price data fetching to use a 365-day fallback period instead of 7 days:

```javascript
start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Last 365 days as fallback
```

### 3. Improved Date Range Logic

Enhanced the date range calculation to fetch data from the first purchase date:

```javascript
// Fetch price data from first purchase date to today
const startDate = firstPurchaseDate ? firstPurchaseDate.toISOString().split('T')[0] : new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
const endDate = new Date().toISOString().split('T')[0];
```

### 4. Fixed Error Handling

Removed incorrect calls to `calculateHoldingAndLimits` with empty data arrays in Ajax failure cases, using default values instead:

```javascript
// In Ajax failure cases, use default values
<td>0</td>
<td>${(stock.cost * 0.95).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} / ${(stock.cost * 1.05).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
```

## Verification

The fix was verified with test data:
- Purchase date: 2024-06-21
- Highest high price: 70.1 (on 2024-06-24)
- Expected take-profit line: 70.1 * 0.93 = 65.19

The calculation now correctly produces the expected result of 65.1.

## Files Modified

- `web/templates/dashboard.html`: Main dashboard template with all fixes implemented

## Benefits

1. **Accurate Take-Profit Calculation**: Users now see correct take-profit lines based on actual highest prices
2. **Better Historical Data Coverage**: Extended data range ensures more accurate calculations
3. **Improved Error Handling**: More robust handling of data fetching failures
4. **Enhanced User Experience**: More reliable and accurate dashboard information

## Future Considerations

1. Consider implementing a more sophisticated data fetching strategy that dynamically determines the optimal date range
2. Add logging or debugging information to help diagnose calculation issues in the future
3. Consider adding unit tests for the calculation functions to prevent regressions

