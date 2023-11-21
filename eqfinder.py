import tkinter as tk
import numpy as np
import time

class GraphApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Drawer")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="white")
        self.canvas.pack()

        self.points = []
        self.line_id = None
        self.equation_label = tk.Label(self.master, text="")
        self.equation_label.pack()

        self.hold_start_time = 0
        self.hold_threshold = 1000  # 1000 milliseconds (1 second)
        self.anchor_point = None

        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.release_button)

        # Create a reset button
        self.reset_button = tk.Button(self.master, text="Reset", command=self.reset_canvas)
        self.reset_button.pack()

        # Draw the coordinate axes
        self.draw_axes()

    def draw_axes(self):
        # Draw the x-axis and y-axis
        self.canvas.create_line(0, 200, 400, 200, fill="black", width=2)
        self.canvas.create_line(200, 0, 200, 400, fill="black", width=2)

        # Draw tick marks for the x-axis
        for i in range(-10, 11):
            x = 200 + i * 20
            self.canvas.create_line(x, 198, x, 202, fill="black")

        # Draw tick marks for the y-axis
        for i in range(-10, 11):
            y = 200 + i * 20
            self.canvas.create_line(198, y, 202, y, fill="black")

    def draw_line(self, event):
        x, y = event.x, event.y
        current_time = time.time()

        # Check if the mouse is held down in the same spot for the specified time
        if current_time - self.hold_start_time >= self.hold_threshold:
            # If held for 1 second, turn the line into a straight line with rotation anchor
            if not self.anchor_point:
                self.anchor_point = (x, y)
            else:
                self.points = [self.anchor_point, (x, y)]

        self.points.append((x, y))

        # Draw line as the user moves the mouse
        if len(self.points) > 1:
            if self.line_id:
                self.canvas.delete(self.line_id)
            self.line_id = self.canvas.create_line(self.points, fill="black")

    def release_button(self, event):
        # Check if the user is holding the mouse button to draw a straight line
        if len(self.points) > 2:
            # Fit a straight line through the points
            coefficients = self.fit_line(self.points)

            # Draw the straight line
            if coefficients:
                x1, y1, x2, y2 = self.get_line_endpoints(coefficients)
                self.canvas.create_line(x1, y1, x2, y2, fill="red")

                # Display the equation of the line
                equation = f"Equation: y = {coefficients[0]:.2f}x + {coefficients[1]:.2f}"
                self.equation_label.config(text=equation)

            # Clear the drawn points and line
            self.points = []
            self.anchor_point = None
            self.canvas.delete(self.line_id)

        # Reset the hold start time
        self.hold_start_time = 0

    def fit_line(self, points):
        try:
            # Fit a straight line through the points using linear regression
            x_coords, y_coords = zip(*points)
            x_coords = np.array(x_coords) - self.anchor_point[0]
            y_coords = np.array(y_coords) - self.anchor_point[1]
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, b = np.linalg.lstsq(A, y_coords, rcond=None)[0]

            # Return the slope and y-intercept
            return m, b + self.anchor_point[1]
        except Exception as e:
            print(f"Failed to fit line: {str(e)}")
            return None

    def get_line_endpoints(self, coefficients):
        # Calculate the endpoints of the line based on the slope and y-intercept
        m, b = coefficients
        x1, y1 = min(self.points, key=lambda p: p[0])
        x2, y2 = max(self.points, key=lambda p: p[0])

        # Calculate y values for the endpoints based on the equation y = mx + b
        y1_calculated = int(m * (x1 - self.anchor_point[0]) + b)
        y2_calculated = int(m * (x2 - self.anchor_point[0]) + b)

        # Return the endpoints
        return x1, y1_calculated, x2, y2_calculated

    def reset_canvas(self):
        # Clear all lines and reset the equation label
        self.canvas.delete("all")
        self.equation_label.config(text="")
        # Draw the coordinate axes again
        self.draw_axes()
        # Reset anchor point
        self.anchor_point = None

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
