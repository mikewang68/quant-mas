// Test MA calculation function
function calculateMA(data, period) {
    if (!data || data.length < period || period <= 0) return [];

    const ma = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            ma.push(null);
        } else {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            ma.push(sum / period);
        }
    }

    return ma;
}

// Test data
const testData = [10, 12, 13, 15, 14, 16, 18, 17, 19, 20];
console.log('Test data:', testData);

// Test MA5 calculation
const ma5 = calculateMA(testData, 5);
console.log('MA5:', ma5);

// Test MA13 calculation (should return all null since we don't have enough data)
const ma13 = calculateMA(testData, 13);
console.log('MA13 (insufficient data):', ma13);

// Test with sufficient data for MA13
const testData2 = [10, 12, 13, 15, 14, 16, 18, 17, 19, 20, 21, 22, 23, 24, 25];
const ma13_2 = calculateMA(testData2, 13);
console.log('MA13 (sufficient data):', ma13_2);

