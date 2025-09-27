// Test MA implementation based on the actual code in stock_kline_v2.html

// Mock fetch function for testing
function mockFetch(url) {
    return new Promise((resolve) => {
        if (url.includes('strategy-by-name')) {
            // Mock strategy data
            const mockData = {
                "_id": "68a6591d8dace06d7edd9582",
                "name": "三均线多头排列策略（宽松型）",
                "parameters": {
                    "ma_long": "34",
                    "ma_mid": "13",
                    "ma_short": "5"
                }
            };
            resolve({
                json: () => Promise.resolve(mockData)
            });
        }
    });
}

// MA calculation function (copied from the actual code)
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
const closes = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110, 112, 111, 113, 115];

// Test the MA parameter fetching and calculation
async function testMAImplementation() {
    console.log('Testing MA implementation...');

    // Default parameters
    let maParams = { short: 5, mid: 13, long: 34 };
    console.log('Default parameters:', maParams);

    try {
        // Simulate fetching strategy parameters
        const response = await mockFetch('/api/strategy-by-name/三均线多头排列策略（宽松型）');
        const strategyData = await response.json();

        if (strategyData && strategyData.parameters) {
            const params = strategyData.parameters;
            maParams = {
                short: parseInt(params.ma_short || params.short || 5),
                mid: parseInt(params.ma_mid || params.mid || 13),
                long: parseInt(params.ma_long || params.long || 34)
            };
            console.log('Fetched parameters:', maParams);
        }

        // Calculate MA lines
        const maShortData = calculateMA(closes, maParams.short);
        const maMidData = calculateMA(closes, maParams.mid);
        const maLongData = calculateMA(closes, maParams.long);

        console.log('MA' + maParams.short + ':', maShortData);
        console.log('MA' + maParams.mid + ':', maMidData);
        console.log('MA' + maParams.long + ':', maLongData);

        console.log('MA implementation test completed successfully!');

    } catch (error) {
        console.error('Error in MA implementation test:', error);
    }
}

// Run the test
testMAImplementation();

