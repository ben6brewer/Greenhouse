import matplotlib.pyplot as plt


class GraphGenerator:

    def create_graph(self, days_elapsed, data):
        temperature_data = data[0]
        humidity_data = data[1]
        print("CG temp data: " + str(temperature_data))
        plt.clf()
        time_array = list(range(len(temperature_data)))
        plt.plot(time_array, temperature_data, marker='o', label='Temperature')
        plt.plot(time_array, humidity_data, marker='o', label='Humidity')

        plt.xlabel('Time (hours)')
        plt.ylabel('Fahrenheit / Relative Humidity')
        plt.title('Greenhouse Day ' + str(days_elapsed))
        plt.legend()
        directory = f'/home/ben6brewer/Desktop/Graphs/Day_{days_elapsed}_Graph.pdf'
        plt.savefig(directory, format='pdf')

