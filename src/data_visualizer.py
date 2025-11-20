from typing import List, Tuple, Dict, Any
from functools import reduce
import matplotlib.pyplot as plt 
import os
import asyncio

try:
    from.models import WeatherRecord
except ImportError:
    from models import WeatherRecord
    
#---------- Data Filtering Function--------------------------------

def filter_hot_days(records: List[WeatherRecord], threshold: float = 25.0) -> List[WeatherRecord]:
    # Filter through the weather record to find the max temp threshold 🔥
    
    def is_hot(record: WeatherRecord) -> bool:
        try:
            # Get the max temp from the records row dictionary
            max_temp_string = record.row.get('MaxTemp', '')
            if not max_temp_string: 
                return False
            max_temp = float(max_temp_string)
            return max_temp > threshold # True if its hot, otherwise its False
        except (ValueError, TypeError):
            return False
    return list(filter(is_hot, records))

def filter_cold_days(records: List[WeatherRecord], threshold: float = 15.0) -> List[WeatherRecord]:
    # Filter through the weather record to find the lowest temp threshold 🥶
    
    def is_cold(record: WeatherRecord) -> bool:
        try:
            # Get the lowest temp from the records row dictionary
            max_temp_string = record.row.get('MaxTemp', '')
            if not max_temp_string: 
                return False
            max_temp = float(max_temp_string)
            return max_temp < threshold # True if its cold, otherwise its False
        except (ValueError, TypeError):
            return False
    return list(filter(is_cold, records))
        
def filter_rainy_days(records: List[WeatherRecord]) -> List[WeatherRecord]:
    # Filter through to find the nice rainy days
    return list(filter(lambda rec: rec.row.get('RainToday', '').strip() =="Yes", records))

def filter_dry_days(records: List[WeatherRecord]) -> List[WeatherRecord]:
    # Filter through to find the dry days
    return list(filter(lambda rec: rec.row.get('RainToday', '').strip() == 'No', records))

#-------------------- Data Extraction Functions --------------------------
def extract_max_temps(records: List[WeatherRecord]) -> List[float]:
    # Use map to extract the MaxTemp from each of the records
    def get_max_temp(record: WeatherRecord) -> float:
        try:
            temp_string = record.row.get('MaxTemp', '')
            if not temp_string:
                return 0.0 #Default in case its missing
            return float(temp_string)
        except (ValueError, TypeError):
            return 0.0
    return list(map(get_max_temp, records))

def extract_min_temps(records: List[WeatherRecord]) -> List[float]:
    # Use map to extract the MinTemp from each of the records
    def get_min_temp(record: WeatherRecord) -> float:
        try:
            temp_string = record.row.get('MinTemp', '')
            if not temp_string:
                return 0.0 #Default in case its missing
            return float(temp_string)
        except (ValueError, TypeError):
            return 0.0
    return list(map(get_min_temp, records))

def extract_rainfall(records: List[WeatherRecord]) -> List[float]:
    # Use map to extract rain fall from each of the records
    def get_rainfall(record: List[WeatherRecord]) -> float:
        try:
            rain_string = record.row.get('Rainfall', '')
            if not rain_string:
                return 0.0 #Default in case its missing
            return float(rain_string)
        except (ValueError, TypeError):
            return 0.0
    return list(map(get_rainfall, records))

#----------------------Aggregation Functions------------------------------------

def calculate_total_rainfall(rainfall_amounts: List[float]) -> float:
    # Use reduce to add up all of the rainfall amounts
    if not rainfall_amounts:
        return 0.0
    return reduce(lambda total, amount: total + amount, rainfall_amounts, 0.0)

def calculate_average_temp(temperatures: List[float]) -> float:
    # Use reduce to calculate the average temperature
    if not temperatures:
        return 0.0
    total = reduce(lambda sum_so_far, temp: sum_so_far + temp, temperatures, 0.0)
    return total / len(temperatures)

def count_days_above_threshold(temperatures: List[float], threshold: float) -> int:
    # Use reduce to count how many days there are exceeding the threshold
    return reduce(
        lambda count, temp: count + (1 if temp > threshold else 0), temperatures, 0
    )

#-----------------New Async chart saving helper phase 7-------------------------------------
async def async_save_plot(output_path: str, fig=None, dpi: int = 300) -> str:
    """Async saves a matplotlib figure to a file"""
    
    def _save_sync():
        """Helper function that will do the actual blocking save"""
        if fig is not None:
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        else:
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig if fig is not None else 'all')
        
    await asyncio.to_thread(_save_sync)
    return output_path
    
#----------------Visualization Functions (edited for phase 7 async) 🙂----------------------------------------

def plot_hot_vs_cold_comparison(records: List[WeatherRecord], output_path: str = "hot_vs_cold.png") -> Dict[str, Any]:
    # This creates a line chart comparing the hot and cold days
    print("Creating Hot vs Cold comparison chart:  ")
    
    hot_days = filter_hot_days(records, threshold=25.0)
    cold_days = filter_cold_days(records, threshold=15.0)
    
    hot_temps = extract_max_temps(hot_days)
    cold_temps = extract_max_temps(cold_days)
    
    average_hot = calculate_average_temp(hot_temps) if hot_temps else 0
    average_cold = calculate_average_temp(cold_temps) if cold_temps else 0
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(range(len(hot_temps)), 
             hot_temps, 
             color="red", 
             label=f"Hot Days (>{25}°C)", 
             alpha=0.7, linewidth=2) 
    
    plt.plot(range(len(cold_temps)), 
             cold_temps, 
             color="blue", 
             label=f"Cold Days (<{15}°C)", 
             alpha=0.7, linewidth=2) 
    
    
    if hot_temps:
        plt.axhline(y=average_hot, 
                    color="red",
                    linestyle="--",
                    label=f"Average Hot: {average_hot:.1f}°C", 
                    alpha=0.5)  
    if cold_temps:
        plt.axhline(y=average_cold, 
                    color="red",
                    linestyle="--",
                    label=f"Average Cold: {average_cold:.1f}°C", 
                    alpha=0.5)      
        
    # Labels and formatting    
    plt.xlabel("Day Index", fontsize=12)
    plt.ylabel("Maximum Temperature (°C)", fontsize=12)
    plt.title("Hot Days vs Cold Days temperature Comparison", fontsize=14, fontweight="bold")
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    
    # Save the chart
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Chart save to: {output_path}")
    
    # Return the statistics results
    return {
        "hot_day_count": len(hot_days),
        "cold_day_count": len(cold_days),
        "average_hot_temp": average_hot,
        "average_cold_days": average_cold,
        "chart_path": output_path
    }
    
def plot_rainy_vs_dry_comparison(records: List[WeatherRecord], output_path: str = "rain_vs_dry.png") -> Dict[str, Any]:
    # This will show patterns and temperature differences between
    # rainy vs dry periods
    
    print("Creating rainy vs dry comparison chart:  ")
    
    rainy_days = filter_rainy_days(records)
    dry_days = filter_dry_days(records)
    
    rainy_amounts = extract_rainfall(rainy_days)
    
    rainy_temps = extract_max_temps(rainy_days)
    dry_temps = extract_max_temps(dry_days)
    
    total_rainfall = calculate_total_rainfall(rainy_amounts)
    average_rainy_temp = calculate_average_temp(rainy_temps) if rainy_temps else 0
    average_dry_temp = calculate_average_temp(dry_temps) if dry_temps else 0
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 16))
    
    # Left Plot. Rainfall amounts on rainy days
    ax1.plot(range(len(rainy_amounts)), rainy_amounts, 
             color="steelblue",
             label="Daily Rainfall",
             linewidth=2)
    ax1.fill_between(range(len(rainy_amounts)), rainy_amounts,
                     alpha=0.3, color="steelblue")
    ax1.set_xlabel("Rain Day Index", fontsize=12)
    ax1.set_ylabel("RainFall (mm)", fontsize=12)
    ax1.set_title("Rainfall Amounts on Rainy Days\nTotal: {total_rainfall:.1f}mm", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Right Plot, temperature comparison
    ax2.plot(range(len(rainy_temps)), 
                   rainy_temps,
                   color="navy",
                   label=f"Dry Days (Average: {average_rainy_temp:.1f}°C)",
                   alpha=0.7,
                   linewidth=2)
    ax2.plot(range(len(dry_temps)),
                       color='orange',
                       label=f'Dry Days (Average: {average_dry_temp:.1f}°C)',
                       alpha=0.7,
                       linewidth=2)
    ax2.set_xlabel('Day Index', fontsize=12)
    ax2.set_ylabel('Maximum Temperature (°C)', fontsize=12)
    ax2.set_title('Temperature: Rainy Days vs Dry Days', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    
    return {
        'rainy_day_count': len(rainy_days),
        'dry_day_count': len(dry_days),
        'total_rainfall': total_rainfall,
        'average_rainy_temp': average_rainy_temp,
        "average_dry_temp": average_dry_temp,
        "chart_path": output_path
    }
#-------------------------Main Analysis Function (Edited it to have async phase 7)--------------------------------------------------------
def analyze_and_visualize(records: List[WeatherRecord], output_directory: str = ".") -> Dict[str, Any]:    
    """Original synchronous version - kept for comparison"""
    print("\n" + "="*60)
    print("Weather Pattern Analysis")
    print("Using: map, filter, reduce, and lambda")
    print("="*60 + "\n")
    
    hot_cold_path = os.path.join(output_directory, "hot_vs_cold.png")
    rainy_dry_path = os.path.join(output_directory, "rainy_vs_dry.png")
    
    #Chart 1. Hot vs cold days
    print("Analyzing hot vs cold temperature patterns:  ")
    hot_cold_stats = plot_hot_vs_cold_comparison(records, hot_cold_path)
    
    # Chart 2. rainy vs dry days
    print("\n Analyzing rainy vs dry weather patterns:  ")
    rainy_dry_stats = plot_rainy_vs_dry_comparison(records, rainy_dry_path)
    
    print("\n Computing additional statistics using map/filter/reduce")
    
    all_max_temps = extract_max_temps(records)
    overall_average = calculate_average_temp(all_max_temps)
    
    very_hot_count = count_days_above_threshold(all_max_temps, 30.0)
    moderate_temps = list(filter(lambda t: 15 <= t <= 25, all_max_temps))
    
    # Summary
    print("\n" + "="*60)
    print("Analysis Complete")
    print("="*60)
    print(f"\n Total Records Analyzed: {len(records)}")
    print(f"\n Temperature Analysis:")
    print(f"   - Overall Average Max Temperature: {overall_average:.1f}°C")
    print(f"   - Hot Days (>25°C): {hot_cold_stats['hot_day_count']}")
    print(f"   - Cold Days (<15°C): {hot_cold_stats['cold_day_count']}")
    print(f"   - Very Hot Days (>30°C): {very_hot_count}")
    print(f"   - Moderate Days (15-25°C): {len(moderate_temps)}")
    
    print(f"\n  Rainfall Analysis:")
    print(f"   - Rainy Days: {rainy_dry_stats['rainy_day_count']}")
    print(f"   - Dry Days: {rainy_dry_stats['dry_day_count']}")
    print(f"   - Total Rainfall: {rainy_dry_stats['total_rainfall']:.1f}mm")
    print(f"   - Average Temperature on Rainy Days: {rainy_dry_stats['average_rainy_temp']:.1f}°C")
    print(f"   - Average Temperature on Dry Days: {rainy_dry_stats['average_dry_temp']:.1f}°C")
    
    print(f"\n Charts saved to:")
    print(f"   - {hot_cold_path}")
    print(f"   - {rainy_dry_path}")
    print(f"\n" + "="*60 + "\n")
    
    return {
        'total_records': len(records),
        'overall_average_temp': overall_average,
        'hot_cold_analysis': hot_cold_stats,
        'rainy_dry_analysis': rainy_dry_stats,
        'very_hot_days': very_hot_count,
        'moderate_days': len(moderate_temps)
    }


#================================ASYNC VERSION PHASE 7===============================================================

async def async_plot_hot_vs_cold_comparison(records: List[WeatherRecord], output_path: str = "hot_vs_cold.png") -> Dict[str, Any]:
    # This creates a line chart comparing the hot and cold days
    print("Creating Hot vs Cold comparison chart:  ")
    
    hot_days = filter_hot_days(records, threshold=25.0)
    cold_days = filter_cold_days(records, threshold=15.0)
    
    hot_temps = extract_max_temps(hot_days)
    cold_temps = extract_max_temps(cold_days)
    
    average_hot = calculate_average_temp(hot_temps) if hot_temps else 0
    average_cold = calculate_average_temp(cold_temps) if cold_temps else 0
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(range(len(hot_temps)), 
             hot_temps, 
             color="red", 
             label=f"Hot Days (>{25}°C)", 
             alpha=0.7, linewidth=2) 
    
    plt.plot(range(len(cold_temps)), 
             cold_temps, 
             color="blue", 
             label=f"Cold Days (<{15}°C)", 
             alpha=0.7, linewidth=2) 
    
    
    if hot_temps:
        plt.axhline(y=average_hot, 
                    color="red",
                    linestyle="--",
                    label=f"Average Hot: {average_hot:.1f}°C", 
                    alpha=0.5)  
    if cold_temps:
        plt.axhline(y=average_cold, 
                    color="red",
                    linestyle="--",
                    label=f"Average Cold: {average_cold:.1f}°C", 
                    alpha=0.5)      
        
    # Labels and formatting    
    plt.xlabel("Day Index", fontsize=12)
    plt.ylabel("Maximum Temperature (°C)", fontsize=12)
    plt.title("Hot Days vs Cold Days temperature Comparison", fontsize=14, fontweight="bold")
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)
    
    # Save the chart
    plt.tight_layout()
    # Added the await to save the chart without blocking the rest
    await async_save_plot(output_path)
    
    print(f"Chart save to: {output_path}")
    
    # Return the statistics results
    return {
        "hot_day_count": len(hot_days),
        "cold_day_count": len(cold_days),
        "average_hot_temp": average_hot,
        "average_cold_days": average_cold,
        "chart_path": output_path
    }
    
async def async_plot_rainy_vs_dry_comparison(records: List[WeatherRecord], output_path: str = "rain_vs_dry.png") -> Dict[str, Any]:
    # This will show patterns and temperature differences between
    # rainy vs dry periods
    
    print("Creating rainy vs dry comparison chart:  ")
    
    rainy_days = filter_rainy_days(records)
    dry_days = filter_dry_days(records)
    
    rainy_amounts = extract_rainfall(rainy_days)
    
    rainy_temps = extract_max_temps(rainy_days)
    dry_temps = extract_max_temps(dry_days)
    
    total_rainfall = calculate_total_rainfall(rainy_amounts)
    average_rainy_temp = calculate_average_temp(rainy_temps) if rainy_temps else 0
    average_dry_temp = calculate_average_temp(dry_temps) if dry_temps else 0
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 16))
    
    # Left Plot. Rainfall amounts on rainy days
    ax1.plot(range(len(rainy_amounts)), rainy_amounts, 
             color="steelblue",
             label="Daily Rainfall",
             linewidth=2)
    ax1.fill_between(range(len(rainy_amounts)), rainy_amounts,
                     alpha=0.3, color="steelblue")
    ax1.set_xlabel("Rain Day Index", fontsize=12)
    ax1.set_ylabel("RainFall (mm)", fontsize=12)
    ax1.set_title("Rainfall Amounts on Rainy Days\nTotal: {total_rainfall:.1f}mm", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Right Plot, temperature comparison
    ax2.plot(range(len(rainy_temps)), 
                   rainy_temps,
                   color="navy",
                   label=f"Dry Days (Average: {average_rainy_temp:.1f}°C)",
                   alpha=0.7,
                   linewidth=2)
    ax2.plot(range(len(dry_temps)),
                       color='orange',
                       label=f'Dry Days (Average: {average_dry_temp:.1f}°C)',
                       alpha=0.7,
                       linewidth=2)
    ax2.set_xlabel('Day Index', fontsize=12)
    ax2.set_ylabel('Maximum Temperature (°C)', fontsize=12)
    ax2.set_title('Temperature: Rainy Days vs Dry Days', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    # Saving the figure without blocking
    await async_save_plot(output_path)
    
    return {
        'rainy_day_count': len(rainy_days),
        'dry_day_count': len(dry_days),
        'total_rainfall': total_rainfall,
        'average_rainy_temp': average_rainy_temp,
        "average_dry_temp": average_dry_temp,
        "chart_path": output_path
    }
    
#------------------------- async version phase 7)--------------------------------------------------------    
async def async_analyze_and_visualize(records: List[WeatherRecord], output_directory: str = ".") -> Dict[str, Any]:    
    # Complete analysis pipeline using functional programming
    print("\n" + "="*60)
    print("Weather Pattern Analysis")
    print("Using: map, filter, reduce, and lambda")
    print("="*60 + "\n")
    
    hot_cold_path = os.path.join(output_directory, "how_vs_cold.png")
    rainy_dry_path = os.path.join(output_directory, "rainy_vs_dry.png")
    
    # Creating both charts concurrently
    print("Creating both charts concurrently...")
    hot_cold_stats, rainy_dry_stats = await asyncio.gather(
        async_plot_hot_vs_cold_comparison(records, hot_cold_path),
        async_plot_rainy_vs_dry_comparison(records, rainy_dry_path)
    )
    
    
    print("\n Computing additional statistics using map/filter/reduce")
    
    all_max_temps = extract_max_temps(records)
    overall_average = calculate_average_temp(all_max_temps)
    
    very_hot_count = count_days_above_threshold(all_max_temps, 30.0)
    moderate_temps = list(filter(lambda t: 15 <= t <= 25, all_max_temps))
    
    # Summary
    print("\n" + "="*60)
    print("Analysis Complete")
    print("="*60)
    print(f"\n Total Records Analyzed: {len(records)}")
    print(f"\n Temperature Analysis:")
    print(f"   - Overall Average Max Temperature: {overall_average:.1f}°C")
    print(f"   - Hot Days (>25°C): {hot_cold_stats['hot_day_count']}")
    print(f"   - Cold Days (<15°C): {hot_cold_stats['cold_day_count']}")
    print(f"   - Very Hot Days (>30°C): {very_hot_count}")
    print(f"   - Moderate Days (15-25°C): {len(moderate_temps)}")
    
    print(f"\n  Rainfall Analysis:")
    print(f"   - Rainy Days: {rainy_dry_stats['rainy_day_count']}")
    print(f"   - Dry Days: {rainy_dry_stats['dry_day_count']}")
    print(f"   - Total Rainfall: {rainy_dry_stats['total_rainfall']:.1f}mm")
    print(f"   - Average Temperature on Rainy Days: {rainy_dry_stats['average_dry_temp']:.1f}°C")
    print(f"   - Average Temperature on Dry Days: {rainy_dry_stats['average_dry_temp']:.1f}°C")
    
    print(f"\n Charts saved to:")
    print(f"   - {hot_cold_path}")
    print(f"   - {rainy_dry_path}")
    print(f"\n" + "="*60 + "\n")
    
    return {
        'total_records': len(records),
        'overall_average_temp': overall_average,
        'hot_cold_analysis': hot_cold_stats,
        'rainy_dry-analysis': rainy_dry_stats,
        'very_hot_days': very_hot_count,
        'moderate_days': len(moderate_temps)
    }