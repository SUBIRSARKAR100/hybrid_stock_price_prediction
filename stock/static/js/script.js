document.addEventListener('DOMContentLoaded', () => {
    const tickerInput = document.getElementById('ticker-input');
    const predictBtn = document.getElementById('predict-btn');
    const dashboard = document.getElementById('dashboard');
    const loader = document.getElementById('loader');
    
    // Architecture Selection Buttons
    const mainArchBtn = document.getElementById('main-arch-btn');
    const altArchBtn = document.getElementById('alt-arch-btn');
    const mainPrediction = document.getElementById('main-prediction');
    const altPrediction = document.getElementById('alt-prediction');
    
    // Main Architecture UI Elements
    const predCard = document.getElementById('pred-card');
    const predictionLabel = document.getElementById('prediction-label');
    const confidenceFill = document.getElementById('confidence-fill');
    const confidenceText = document.getElementById('confidence-text');
    
    const sentimentLabel = document.getElementById('sentiment-label');
    const sentimentScore = document.getElementById('sentiment-score');

    
    let chartInstance = null;
    let currentTicker = null;  // Store ticker for alternative prediction

    // Architecture Selection Event Listeners
    mainArchBtn.addEventListener('click', () => {
        mainArchBtn.classList.add('active');
        altArchBtn.classList.remove('active');
        mainPrediction.classList.remove('hidden');
        altPrediction.classList.add('hidden');
    });

    altArchBtn.addEventListener('click', async () => {
        altArchBtn.classList.add('active');
        mainArchBtn.classList.remove('active');
        mainPrediction.classList.add('hidden');
        altPrediction.classList.remove('hidden');
        
        // Fetch alternative prediction if not already loaded
        if (currentTicker && altPrediction.dataset.loaded !== 'true') {
            await handleAlternativePrediction(currentTicker);
        }
    });

    // Trigger prediction on button click
    predictBtn.addEventListener('click', handlePrediction);

    // Trigger prediction on Enter key press in input
    tickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handlePrediction();
        }
    });

    async function handlePrediction() {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            alert('Please enter a valid stock ticker or company name.');
            return;
        }

        currentTicker = ticker;
        altPrediction.dataset.loaded = 'false'; // Reset for new prediction

        // Show Loader, Hide Other Screens
        dashboard.classList.add('hidden');
        loader.classList.remove('hidden');
        predictBtn.disabled = true;
        
        // Reset to main architecture view
        mainArchBtn.classList.add('active');
        altArchBtn.classList.remove('active');
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker: ticker }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch prediction');
            }

            // Update UI elements with prediction results
            updateDashboard(data);
            
            // Show Dashboard
            loader.classList.add('hidden');
            dashboard.classList.remove('hidden');
            dashboard.classList.add('fade-in');
        } catch (error) {
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
            // Revert back to initial state
            loader.classList.add('hidden');
        } finally {
            predictBtn.disabled = false;
        }
    }

    async function handleAlternativePrediction(ticker) {
        try {
            const response = await fetch('/predict-alternative', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker: ticker }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch alternative prediction');
            }

            // Update alternative prediction UI
            updateAlternativeDashboard(data);
            altPrediction.dataset.loaded = 'true'; // Mark as loaded
        } catch (error) {
            console.error('Error:', error);
            alert(`Error fetching alternative prediction: ${error.message}`);
        }
    }

    function updateDashboard(data) {

        // Prediction outcome formatting
        const isBullish = data.prediction === 1;
        predictionLabel.textContent = data.predictionLabel;
        
        if (isBullish) {
            predCard.className = 'card glass prediction-card bullish';
        } else {
            predCard.className = 'card glass prediction-card bearish';
        }

        // Confidence progress bar
        const confidenceVal = Math.round(data.confidence);
        confidenceText.textContent = `${confidenceVal}%`;
        confidenceFill.style.width = `${confidenceVal}%`;

        // Prediction Explanation
        const explanationElement = document.getElementById('prediction-explanation');
        explanationElement.textContent = data.explanation;

        // Sentiment display
        sentimentLabel.textContent = data.sentimentLabel;
        sentimentLabel.className = 'sentiment-value'; // Reset
        
        if (data.sentimentLabel.toLowerCase() === 'positive') {
            sentimentLabel.classList.add('sentiment-positive');
        } else if (data.sentimentLabel.toLowerCase() === 'negative') {
            sentimentLabel.classList.add('sentiment-negative');
        } else {
            sentimentLabel.classList.add('sentiment-neutral');
        }
        
        sentimentScore.textContent = data.sentimentScore.toFixed(2);


    }

    function updateAlternativeDashboard(data) {
        // Update 1-Day Sentiment
        const sentiment1Day = document.getElementById('sentiment-1day');
        sentiment1Day.textContent = data.sentiment1Day === 1 ? 'POSITIVE ✅' : 'NEGATIVE ❌';
        sentiment1Day.className = 'flow-value ' + (data.sentiment1Day === 1 ? 'positive' : 'negative');

        // Update 3-Day Sentiment
        const sentiment3Day = document.getElementById('sentiment-3day');
        sentiment3Day.textContent = data.sentiment3Day === 1 ? 'POSITIVE ✅' : 'NEGATIVE ❌';
        sentiment3Day.className = 'flow-value ' + (data.sentiment3Day === 1 ? 'positive' : 'negative');

        // Update Sentiment OR Logic equation
        document.getElementById('sentiment-1day-val').textContent = data.sentiment1Day;
        document.getElementById('sentiment-3day-val').textContent = data.sentiment3Day;
        document.getElementById('sentiment-or-val').textContent = data.sentimentConfirmation;
        
        const sentimentOrEquation = document.getElementById('sentiment-or-equation');
        sentimentOrEquation.className = 'flow-equation ' + (data.sentimentConfirmation === 1 ? 'positive' : 'negative');

        // Update Technical Signal
        const technicalSignalDisplay = document.getElementById('technical-signal-display');
        technicalSignalDisplay.textContent = data.technicalSignal === 1 ? 'BULLISH ✅' : 'BEARISH ❌';
        technicalSignalDisplay.className = 'flow-value ' + (data.technicalSignal === 1 ? 'positive' : 'negative');

        // Update Final AND Logic equation
        document.getElementById('technical-signal-val').textContent = data.technicalSignal;
        document.getElementById('sentiment-confirmation-val').textContent = data.sentimentConfirmation;
        document.getElementById('final-output-val').textContent = data.finalOutput;
        
        const finalAndEquation = document.getElementById('final-and-equation');
        finalAndEquation.className = 'flow-equation ' + (data.finalOutput === 1 ? 'positive' : 'negative');

        // Update Final Result
        const finalSignalDisplay = document.getElementById('final-signal-display');
        finalSignalDisplay.textContent = data.finalSignal;
        finalSignalDisplay.className = 'final-signal ' + (data.finalOutput === 1 ? 'buy-signal' : 'no-buy-signal');
    }

    function renderChart(chartData) {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        // Destroy existing chart if it exists to avoid overlapping
        if (chartInstance) {
            chartInstance.destroy();
        }

        // Style overrides for dark mode chart
        const gridColor = 'rgba(255, 255, 255, 0.05)';
        const labelColor = '#94a3b8';

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.dates,
                datasets: [
                    {
                        label: 'Stock Price',
                        data: chartData.prices,
                        borderColor: '#3b82f6',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: '#3b82f6',
                        pointHoverBorderColor: '#ffffff',
                        tension: 0.15,
                        fill: false
                    },
                    {
                        label: 'SMA 20',
                        data: chartData.sma20,
                        borderColor: '#8b5cf6',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        tension: 0.15,
                        fill: false
                    },
                    {
                        label: 'SMA 50',
                        data: chartData.sma50,
                        borderColor: '#f59e0b',
                        borderWidth: 1.5,
                        borderDash: [3, 3],
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        tension: 0.15,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: false // Using custom HTML legend
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#f8fafc',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        borderWidth: 1,
                        padding: 10,
                        boxPadding: 4,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: gridColor,
                            borderColor: gridColor
                        },
                        ticks: {
                            color: labelColor,
                            maxTicksLimit: 8,
                            font: {
                                family: 'Outfit'
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: gridColor,
                            borderColor: gridColor
                        },
                        ticks: {
                            color: labelColor,
                            font: {
                                family: 'Outfit'
                            },
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
});
