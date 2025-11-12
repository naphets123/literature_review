// Stock Broker Simulation - Frontend JavaScript

let currentFilter = 'all';
let allAssets = [];
let currentAsset = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    startDataRefresh();
});

function initializeApp() {
    fetchEconomicState();
    fetchAssets();
    fetchPortfolio();
}

function setupEventListeners() {
    // Simulation controls
    document.getElementById('startBtn').addEventListener('click', startSimulation);
    document.getElementById('stopBtn').addEventListener('click', stopSimulation);
    document.getElementById('speedSlider').addEventListener('input', updateSimulationSpeed);

    // Asset filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            renderAssets();
        });
    });

    // Modal controls
    const modal = document.getElementById('tradeModal');
    const closeBtn = document.querySelector('.close');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    // Trade form
    document.getElementById('tradeQuantity').addEventListener('input', updateEstimatedTotal);
    document.getElementById('executeTrade').addEventListener('click', executeTrade);
}

// Fetch data functions
async function fetchEconomicState() {
    try {
        const response = await fetch('/api/economic_state');
        const data = await response.json();
        updateEconomicDisplay(data);
    } catch (error) {
        console.error('Error fetching economic state:', error);
    }
}

async function fetchAssets() {
    try {
        const response = await fetch('/api/assets');
        allAssets = await response.json();
        renderAssets();
    } catch (error) {
        console.error('Error fetching assets:', error);
    }
}

async function fetchPortfolio() {
    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        updatePortfolioDisplay(data);
    } catch (error) {
        console.error('Error fetching portfolio:', error);
    }
}

// Update display functions
function updateEconomicDisplay(data) {
    document.getElementById('interestRate').textContent = `${data.interest_rate}%`;
    document.getElementById('unemployment').textContent = `${data.unemployment_rate}%`;

    const sentimentEl = document.getElementById('sentiment');
    sentimentEl.textContent = data.sentiment.toFixed(2);
    sentimentEl.style.color = data.sentiment >= 0 ? '#10b981' : '#ef4444';

    document.getElementById('inflation').textContent = `${data.inflation_rate}%`;
    document.getElementById('gdpGrowth').textContent = `${data.gdp_growth}%`;
    document.getElementById('timeStep').textContent = data.time_step;

    // Update button states
    document.getElementById('startBtn').disabled = data.simulation_running;
    document.getElementById('stopBtn').disabled = !data.simulation_running;
}

function updatePortfolioDisplay(data) {
    const summary = data.summary;

    // Update summary stats
    document.getElementById('totalValue').textContent = formatCurrency(summary.total_value);
    document.getElementById('cash').textContent = formatCurrency(summary.cash);
    document.getElementById('positionsValue').textContent = formatCurrency(summary.positions_value);

    const pnlEl = document.getElementById('totalPnl');
    pnlEl.textContent = formatCurrency(summary.total_pnl);
    pnlEl.className = 'stat-value ' + (summary.total_pnl >= 0 ? 'positive' : 'negative');

    const returnEl = document.getElementById('returnPercent');
    returnEl.textContent = `${summary.total_return_percent.toFixed(2)}%`;
    returnEl.className = 'stat-value ' + (summary.total_return_percent >= 0 ? 'positive' : 'negative');

    // Update positions
    renderPositions(data.positions);
}

function renderAssets() {
    const container = document.getElementById('assetListContainer');

    // Filter assets
    let filteredAssets = allAssets;
    if (currentFilter !== 'all') {
        filteredAssets = allAssets.filter(asset => asset.type === currentFilter);
    }

    // Render
    container.innerHTML = filteredAssets.map(asset => {
        let detailsHtml = '';
        if (asset.type === 'stock') {
            detailsHtml = `${asset.sector} | Beta: ${asset.beta}`;
        } else if (asset.type === 'bond') {
            detailsHtml = `Coupon: ${asset.coupon_rate}% | Maturity: ${asset.maturity_years.toFixed(1)}y`;
        } else if (asset.type === 'option') {
            detailsHtml = `${asset.option_type.toUpperCase()} | Strike: $${asset.strike_price} | Expires: ${asset.expiry_years.toFixed(2)}y`;
        }

        let changeHtml = '';
        if (asset.type === 'stock' && asset.change_percent !== undefined) {
            const changeClass = asset.change_percent >= 0 ? 'positive' : 'negative';
            const changeSign = asset.change_percent >= 0 ? '+' : '';
            changeHtml = `<div class="price-change ${changeClass}">${changeSign}${asset.change_percent.toFixed(2)}%</div>`;
        }

        return `
            <div class="asset-item" data-symbol="${asset.symbol}">
                <div class="asset-info">
                    <div class="asset-symbol">${asset.symbol}</div>
                    <div class="asset-name">${asset.name}</div>
                    <div class="asset-details">${detailsHtml}</div>
                </div>
                <div class="asset-price">
                    <div class="price-value">$${asset.price.toFixed(2)}</div>
                    ${changeHtml}
                </div>
                <div>
                    <button class="btn btn-buy" onclick="openTradeModal('${asset.symbol}', 'buy')">Buy</button>
                </div>
            </div>
        `;
    }).join('');
}

function renderPositions(positions) {
    const container = document.getElementById('positionsContainer');

    if (positions.length === 0) {
        container.innerHTML = '<p class="empty-message">No positions yet. Start by buying some assets!</p>';
        return;
    }

    container.innerHTML = positions.map(pos => {
        const pnlClass = pos.unrealized_pnl >= 0 ? 'positive' : 'negative';
        const pnlSign = pos.unrealized_pnl >= 0 ? '+' : '';

        return `
            <div class="position-item">
                <div class="position-header">
                    <div>
                        <div class="asset-symbol">${pos.symbol}</div>
                        <div class="asset-details">${pos.asset_type}</div>
                    </div>
                    <button class="btn btn-sell" onclick="openTradeModal('${pos.symbol}', 'sell')">Sell</button>
                </div>
                <div class="position-details">
                    <div class="position-detail">
                        <span>Quantity:</span>
                        <span>${pos.quantity.toFixed(4)}</span>
                    </div>
                    <div class="position-detail">
                        <span>Avg Price:</span>
                        <span>$${pos.average_price.toFixed(2)}</span>
                    </div>
                    <div class="position-detail">
                        <span>Current Price:</span>
                        <span>$${pos.current_price.toFixed(2)}</span>
                    </div>
                    <div class="position-detail">
                        <span>Market Value:</span>
                        <span>$${pos.market_value.toFixed(2)}</span>
                    </div>
                </div>
                <div class="position-pnl ${pnlClass}">
                    P&L: ${pnlSign}$${Math.abs(pos.unrealized_pnl).toFixed(2)} (${pnlSign}${pos.unrealized_pnl_percent.toFixed(2)}%)
                </div>
            </div>
        `;
    }).join('');
}

// Modal functions
function openTradeModal(symbol, action) {
    currentAsset = allAssets.find(asset => asset.symbol === symbol);
    if (!currentAsset) return;

    const modal = document.getElementById('tradeModal');
    document.getElementById('modalSymbol').textContent = symbol;
    document.getElementById('modalAssetName').textContent = currentAsset.name;
    document.getElementById('modalPrice').textContent = currentAsset.price.toFixed(2);
    document.getElementById('tradeAction').value = action;
    document.getElementById('tradeQuantity').value = '1';
    document.getElementById('tradeMessage').style.display = 'none';

    updateEstimatedTotal();
    modal.style.display = 'block';
}

function updateEstimatedTotal() {
    if (!currentAsset) return;

    const quantity = parseFloat(document.getElementById('tradeQuantity').value) || 0;
    const total = quantity * currentAsset.price;
    document.getElementById('estimatedTotal').textContent = formatCurrency(total);
}

async function executeTrade() {
    const action = document.getElementById('tradeAction').value;
    const quantity = parseFloat(document.getElementById('tradeQuantity').value);
    const messageEl = document.getElementById('tradeMessage');

    if (!currentAsset || quantity <= 0) {
        showTradeMessage('Invalid quantity', false);
        return;
    }

    try {
        const response = await fetch('/api/trade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: action,
                symbol: currentAsset.symbol,
                quantity: quantity
            })
        });

        const result = await response.json();

        if (result.success) {
            showTradeMessage(result.message, true);
            // Refresh data
            fetchPortfolio();
            fetchAssets();

            // Close modal after 2 seconds
            setTimeout(() => {
                document.getElementById('tradeModal').style.display = 'none';
            }, 2000);
        } else {
            showTradeMessage(result.message, false);
        }
    } catch (error) {
        showTradeMessage('Error executing trade', false);
        console.error('Trade error:', error);
    }
}

function showTradeMessage(message, success) {
    const messageEl = document.getElementById('tradeMessage');
    messageEl.textContent = message;
    messageEl.className = 'trade-message ' + (success ? 'success' : 'error');
}

// Simulation controls
async function startSimulation() {
    try {
        await fetch('/api/simulation/start', {method: 'POST'});
        fetchEconomicState();
    } catch (error) {
        console.error('Error starting simulation:', error);
    }
}

async function stopSimulation() {
    try {
        await fetch('/api/simulation/stop', {method: 'POST'});
        fetchEconomicState();
    } catch (error) {
        console.error('Error stopping simulation:', error);
    }
}

async function updateSimulationSpeed() {
    const speed = parseFloat(document.getElementById('speedSlider').value);
    document.getElementById('speedDisplay').textContent = `${speed.toFixed(1)}x`;

    try {
        await fetch('/api/simulation/speed', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({speed: speed})
        });
    } catch (error) {
        console.error('Error updating speed:', error);
    }
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Auto-refresh data
function startDataRefresh() {
    setInterval(() => {
        fetchEconomicState();
        fetchAssets();
        fetchPortfolio();
    }, 1000); // Refresh every second
}
