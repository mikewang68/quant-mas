# Dashboard Recent Trades Profit/Loss Calculation Enhancement

## Overview

This document describes the enhancement made to the dashboard's recent trades section to properly calculate and display profit/loss for buy and sell transactions.

## Problem Description

The previous implementation of the recent trades section in the dashboard had the following issues:
1. All transactions showed "待计算" (pending calculation) for profit/loss
2. Buy transactions should show commission costs as negative values
3. Sell transactions should calculate profit/loss based on average cost basis
4. The calculation needed to handle multiple buy/sell transactions for the same stock

## Solution Implementation

### 1. Added Profit/Loss Calculation Function

A new `calculateTradeProfitLoss` function was implemented to handle the complex calculation logic:

```javascript
function calculateTradeProfitLoss(orders, currentOrder) {
    // Filter orders for the same stock and sort by date
    const stockOrders = orders.filter(order => order.code === currentOrder.code)
                              .sort((a, b) => new Date(a.date) - new Date(b.date));

    // If this is a buy order, return commission as negative value
    if (currentOrder.quantity > 0) {
        const commission = currentOrder.commission || 0;
        return -commission;
    }

    // This is a sell order, calculate profit/loss based on average cost
    let totalQuantity = 0;
    let totalCost = 0;

    // Process orders chronologically to calculate average cost
    for (const order of stockOrders) {
        // Stop processing once we reach the current order
        if (order._id === currentOrder._id) {
            break;
        }

        if (order.quantity > 0) {
            // Buy order - add to position
            totalQuantity += order.quantity;
            totalCost += order.quantity * order.price;
        } else {
            // Sell order - reduce position
            const sellQuantity = Math.abs(order.quantity);
            if (totalQuantity > 0) {
                const averageCost = totalCost / totalQuantity;
                totalQuantity -= sellQuantity;
                totalCost -= sellQuantity * averageCost;

                // Ensure we don't go below zero
                if (totalQuantity < 0) {
                    totalQuantity = 0;
                    totalCost = 0;
                }
            }
        }
    }

    // Calculate profit/loss for current sell order
    if (totalQuantity > 0) {
        const averageCost = totalCost / totalQuantity;
        const sellQuantity = Math.abs(currentOrder.quantity);
        const sellRevenue = sellQuantity * currentOrder.price;
        const sellCost = sellQuantity * averageCost;
        const commission = currentOrder.commission || 0;
        const profitLoss = sellRevenue - sellCost - commission;

        return profitLoss;
    }

    // No previous buy orders or position already closed
    // Still consider commission even if no previous buys
    const commission = currentOrder.commission || 0;
    return -commission;
}
```

### 2. Enhanced Recent Trades Display Logic

The `loadTradingRecords` function was updated to properly display profit/loss information:

```javascript
// Calculate profit/loss for both buy and sell orders
let profitLossText = '';
if (order.quantity < 0) {
    // This is a sell order, calculate profit/loss
    const profitLoss = calculateTradeProfitLoss(accountOrders, order);
    if (profitLoss !== null) {
        const formattedProfitLoss = profitLoss.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        const profitLossClass = profitLoss >= 0 ? 'text-success' : 'text-danger';
        profitLossText = `<span class="${profitLossClass}">${profitLoss >= 0 ? '+' : ''}${formattedProfitLoss}</span>`;
    }
} else {
    // This is a buy order, show commission cost as negative value
    const commission = order.commission || 0;
    if (commission > 0) {
        const formattedCommission = commission.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        profitLossText = `<span class="text-danger">-${formattedCommission}</span>`;
    } else {
        profitLossText = `<span class="text-danger">0.00</span>`;
    }
}
```

## Features

1. **Buy Transactions**: Display commission costs as negative values with red coloring
2. **Sell Transactions**: Calculate profit/loss using average cost basis with proper thousand separators
3. **Commission Handling**: Both buy and sell transactions properly account for commission costs
4. **Color Coding**:
   - Green for profits (+)
   - Red for losses (-)
5. **Thousand Separators**: All monetary values display with proper thousand separators
6. **Right Alignment**: Profit/loss values are right-aligned for better readability
7. **Multiple Transactions Handling**: Properly handles multiple buy/sell transactions for the same stock
8. **Position Tracking**: Correctly tracks position changes to prevent duplicate calculations

## Benefits

1. **Accurate Profit/Loss Calculation**: Users now see correct profit/loss values for their transactions
2. **Better Visualization**: Color-coded display makes it easy to distinguish profits from losses
3. **Proper Formatting**: Thousand separators improve readability of monetary values
4. **Complete Transaction Information**: Both buy and sell transactions now show relevant financial information
5. **Commission Consideration**: All transactions properly account for commission costs
6. **Improved Layout**: Right-aligned profit/loss values enhance table readability

## Files Modified

- `web/templates/dashboard.html`: Main dashboard template with all fixes implemented

## Verification

The implementation was tested with various scenarios:
1. Single buy transaction
2. Single sell transaction
3. Multiple buy transactions followed by sell
4. Partial position sells
5. Complete position sells and re-buys
6. Transactions with and without commission data

All scenarios correctly displayed the expected profit/loss values with proper formatting and coloring.

