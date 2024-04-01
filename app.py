import json
import datetime
import matplotlib.pyplot as plt
import peakutils
import numpy as np
from PIL import Image, ImageFilter
import matplotlib.patheffects as patheffects
from flask import Flask, send_file
from flask import request, render_template

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = json.loads(request.form.get('jsondata'))
    invoices = data['props']['invoices']['data']

    # Extract x and y values from the data
    x_values = [datetime.datetime.strptime(item['from'], "%Y-%m-%d %H:%M:%S") for item in invoices]
    y_values = [float(item['formatted_total'].replace('$', '')) for item in invoices]

    plt.close('all')
    plt.switch_backend('agg')

    # Create the graph
    plt.style.use('dark_background')

    plt.plot(x_values, y_values)
    plt.xlabel('Date')
    # Convert y_values to a NumPy array
    y_values = np.array(y_values)

    plt.ylabel('Amount in $')
    plt.title('Total revenue: $' + str(sum(y_values)) + ' USD')
    plt.xticks(rotation=20)  # Rotate x-axis labels by 20 degrees
    plt.tight_layout()  # Adjust the layout to prevent labels from being cut off

    # Find peaks in the y_values
    indexes = peakutils.indexes(y_values, thres=0.2, min_dist=3).astype(int)  # Convert indexes to integers

    # Add horizontal dotted lines for each peak
    for index in indexes:
        plt.annotate(f'{y_values[index]:.2f}', xy=(x_values[index], y_values[index]), xytext=(-30, 10),
                    textcoords='offset points', arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=12, fontweight='bold', color='white', path_effects=[patheffects.withStroke(linewidth=3, foreground='red')])

    # Add a line connecting the peaks
    peak_line_x = [x_values[index] for index in indexes]
    peak_line_y = [y_values[index] for index in indexes]
    plt.plot(peak_line_x, peak_line_y, 'r--', path_effects=[patheffects.withStroke(linewidth=3, foreground='red')])
    
    plt.savefig('static/graph.png', dpi=800)

    # Compress the saved image
    image = Image.open('static/graph.png')
    image.save('static/graph.png', optimize=True, quality=50)

    return {'code': 200, 'message': 'Graph created successfully!', 'path': '/static/graph.png'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)