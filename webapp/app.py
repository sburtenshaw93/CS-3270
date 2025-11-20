""" 
Module 9 Phase 9
Flask Web Application
"""

from flask import Flask, render_template, request, jsonify
from models import get_session, WeatherRecord, UserQuery
from database import get_statistics, log_user_query
from ml_model import predict_rain
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

#Create flask app
app = Flask(__name__)

# Path for saving the charts
CHART_DIR = Path(__file__).parent / 'static' / 'charts'
CHART_DIR.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """ 
    Home page 
    """
    stats = get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/statistics')
def statistics():
    """ 
    Statistics page
    """
    stats = get_statistics()
    # Log this query 
    log_user_query('view_statistics', {}, stats['total_records'] if stats else 0)
    
    return render_template('statistics.html', stats=stats)

@app.route('/filter', methods=['GET', 'POST'])
def filter_data():
    """ 
    Filter the weather data base on the user input
    """
    if request.method == 'POST':
        # Get filter parameters from form
        min_temp = request.form.get('min_temp', type=float)
        max_temp = request.form.get('max_temp', type=float)
        
        # Query database
        session = get_session()
        query = session.query(WeatherRecord)
        
        if min_temp is not None:
            query = query.filter(WeatherRecord.max_temp >= min_temp)
        if max_temp is not None:
            query = query.filter(WeatherRecord.max_temp <= max_temp)
        
        results = query.limit(100).all()
        session.close()
        
        # Log the query
        log_user_query('filter', {'min': min_temp, 'max': max_temp}, len(results))
        
        # Render results
        return render_template('filter.html', results=results,
                               min_temp=min_temp, max_temp=max_temp)
    
    return render_template('filter.html', results=None)

@app.route('/visualizations')
def visualization():
    """ 
    Create and display charts
    """
    # Get data from database
    session = get_session()
    records = session.query(WeatherRecord).limit(500).all()
    session.close()
    
    if not records:
        return render_template('visualizations.html', chart_created=False)
    
    # Create hot vs cold chart
    hot_days = [r for r in records if r.max_temp and r.max_temp > 25]
    cold_days = [r for r in records if r.max_temp and r.max_temp < 15]
    
    hot_temps = [r.max_temp for r in hot_days]
    cold_temps = [r.max_temp for r in cold_days]
    
    # Create chart
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(hot_temps)), hot_temps, 'r-', label='Hot Days (>25°C)', alpha=0.7)
    plt.plot(range(len(cold_temps)), cold_temps, 'b-', label='Cold Days (<15°C)', alpha=0.7)
    plt.xlabel('Day Index')
    plt.ylabel('Temperature (°C)')
    plt.title('Hot vs Cold Days Comparison')
    plt.grid(True, alpha=0.3)
    
    # Save chart
    chart_path = CHART_DIR / 'hot_vs_cold.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Log visualization view
    log_user_query('view_visualization', {}, len(records))
    
    return render_template('visualizations.html',
                           chart_created=True,
                           hot_count = len(hot_days),
                           cold_count = len(cold_days))
    
@app.route('/api/stats')
def api_stats():
    """ 
    API endpoint - returns JSON data
    """    
    stats = get_statistics()
    return jsonify(stats)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """ 
    ML Prediction page - predicts if it will rain tomorrow
    """
    prediction_result = None
    
    if request.method == "POST":
        # Get form data
        location = request.form.get('location', 'Sydney')
        min_temp = request.form.get('min_temp', type=float)
        max_temp = request.form.get('max_temp', type=float)
        rainfall = request.form.get('rainfall', type=float)
        rain_today = request.form.get('rain_today', 'No')
        
        # Make prediction
        prediction_result = predict_rain(
            location=location,
            min_temp=min_temp,
            max_temp=max_temp,
            rainfall=rainfall,
            rain_today=rain_today
        )
        
        # Add input data to the result
        prediction_result['inputs'] = {
            'location': location,
            'min_temp': min_temp, 
            'max_temp': max_temp,
            'rainfall': rainfall,
            'rain_today': rain_today
        }
        #Log the prediction query
        log_user_query('ml_prediction', prediction_result['inputs'], 1)
    
    return render_template('predict.html', result=prediction_result)
    

if __name__ == "__main__":
    print("="*60)
    print("Starting Weather Web Application")
    print("="*60)
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, port=5000)
    