// Test data based on user's example
const stockOrders = [
    { date: "2024-06-21" }
];

const priceData = [
    { date: "2024-06-21", high: 65.0, close: 64.5 },
    { date: "2024-06-24", high: 70.1, close: 69.8 },
    { date: "2024-06-25", high: 68.5, close: 68.0 },
    { date: "2024-06-26", high: 67.2, close: 66.8 },
    { date: "2024-06-27", high: 66.0, close: 65.5 },
    { date: "2024-06-28", high: 64.8, close: 64.3 },
    { date: "2024-07-01", high: 63.5, close: 63.0 },
    { date: "2024-07-02", high: 62.8, close: 62.3 },
    { date: "2024-07-03", high: 61.5, close: 61.0 },
    { date: "2024-07-04", high: 60.2, close: 59.8 },
    { date: "2024-07-05", high: 59.0, close: 58.5 }
];

const cost = 58.8;

// Sort orders by date
stockOrders.sort((a, b) => new Date(a.date) - new Date(b.date));

// Calculate holding days (days since first purchase)
let holdingDays = 0;
let firstPurchaseDate = null;
if (stockOrders.length > 0) {
    firstPurchaseDate = new Date(stockOrders[0].date);
    const today = new Date();
    holdingDays = Math.floor((today - firstPurchaseDate) / (1000 * 60 * 60 * 24));
}

// Calculate stop-loss line (cost basis * 0.95)
const stopLossLine = (cost || 0) * 0.95;

// Calculate take-profit line (highest price since opening position * 0.93)
let takeProfitLine = (cost || 0) * 1.05; // Default to 5% above cost if no price data

// Process orders to track highest price since opening position
if (stockOrders.length > 0 && priceData.length > 0 && firstPurchaseDate) {
    // Find the highest price since the first purchase
    let highestPrice = 0;
    priceData.forEach(item => {
        const itemDate = new Date(item.date);
        console.log(`Comparing ${item.date} (${itemDate}) with first purchase date ${firstPurchaseDate}`);
        console.log(`itemDate >= firstPurchaseDate: ${itemDate >= firstPurchaseDate}`);
        console.log(`item.high (${item.high}) > highestPrice (${highestPrice}): ${item.high > highestPrice}`);
        if (itemDate >= firstPurchaseDate && item.high > highestPrice) {
            highestPrice = item.high;
            console.log(`New highest price: ${highestPrice}`);
        }
    });

    // If we found a higher price, use it for take-profit calculation
    if (highestPrice > 0) {
        takeProfitLine = highestPrice * 0.93;
    }
}

console.log(`Holding days: ${holdingDays}`);
console.log(`Stop-loss line: ${stopLossLine.toFixed(2)}`);
console.log(`Take-profit line: ${takeProfitLine.toFixed(2)}`);
console.log(`Expected take-profit line: ${(70.1 * 0.93).toFixed(2)}`);

