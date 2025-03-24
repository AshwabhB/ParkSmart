import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def plot_parking_data():
    garages = ['North Garage', 'South Garage', 'West Garage', 'South Campus Garage']
    garage_files = [f"{garage.replace(' ', '_').lower()}.csv" for garage in garages]
    
    fig, axes = plt.subplots(4, 2, figsize=(20, 24))
    fig.suptitle('SJSU Parking Garage Occupancy by Day of Week', fontsize=16, y=0.95)
    
    axes = axes.flatten()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    garage_colors = {
        'North Garage': 'blue',
        'South Garage': 'green',
        'West Garage': 'purple',
        'South Campus Garage': 'orange'
    }
    
    all_data = []
    for file in garage_files:
        try:
            df = pd.read_csv(file)
            all_data.append(df)
        except FileNotFoundError:
            print(f"Warning: {file} not found, skipping...")
            continue
    
    if not all_data:
        print("No data files found!")
        return
        
    df = pd.concat(all_data)
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Day'] = df['Timestamp'].dt.day_name()
    df['Hour'] = df['Timestamp'].dt.hour
    
    hours = list(range(24))  
    hour_labels = [f"{h:02d}:00" for h in hours]  
    
    for idx, day in enumerate(days):
        if idx < 7:  
            day_data = df[df['Day'] == day]
            
            for garage in garages:
                garage_day_data = day_data[day_data['Garage Name'] == garage]
                if not garage_day_data.empty:
                    garage_day_data = garage_day_data.sort_values('Hour')
                    
                    line = axes[idx].plot(garage_day_data['Hour'], 
                                        garage_day_data['Occupancy'],
                                        label=garage,
                                        color=garage_colors[garage],
                                        linewidth=2,
                                        alpha=0.6)
                    
                    for x, y in zip(garage_day_data['Hour'], garage_day_data['Occupancy']):
                        color = 'red' if float(y) > 85 else garage_colors[garage]
                        axes[idx].scatter(x, y, color=color, s=50, zorder=5)
            
            axes[idx].set_title(f'{day}', fontsize=12, pad=10)
            axes[idx].set_xlabel('Time', fontsize=10)
            axes[idx].set_ylabel('Occupancy (%)', fontsize=10)
            axes[idx].grid(True, linestyle='--', alpha=0.7)
            
            axes[idx].set_xticks(hours)
            axes[idx].set_xticklabels(hour_labels, rotation=45)
            axes[idx].set_xlim(-0.5, 23.5)  
            axes[idx].set_ylim(0, 100)
            
            axes[idx].axhline(y=85, color='red', linestyle='--', alpha=0.3)
            
            axes[idx].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    if len(axes) > 7:
        fig.delaxes(axes[7])
    
    plt.tight_layout()
    
    plt.savefig('parking_occupancy_by_day.png', bbox_inches='tight', dpi=300)
    print("Plot has been saved as 'parking_occupancy_by_day.png'")
    
    plt.show()

if __name__ == "__main__":
    plot_parking_data() 