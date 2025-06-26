import tkinter as tk
from tkinter import simpledialog, filedialog
from PIL import Image, ImageTk
import json

class ROIEditor:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("ROI Polygon Editor")

        self.image = Image.open(image_path)
        self.tk_image = ImageTk.PhotoImage(self.image)

        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.current_polygon = []
        self.rois = []

        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Double-Button-1>", self.complete_polygon)

        save_btn = tk.Button(root, text="Save to JSON", command=self.save_to_json)
        save_btn.pack(pady=10)

    def add_point(self, event):
        x, y = event.x, event.y
        self.current_polygon.append([x, y])
        self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")

        if len(self.current_polygon) > 1:
            self.canvas.create_line(*self.current_polygon[-2], x, y, fill="blue")

    def complete_polygon(self, event):
        if len(self.current_polygon) < 3:
            print("Polygon needs at least 3 points.")
            return

        # Close the polygon
        self.canvas.create_line(*self.current_polygon[-1], *self.current_polygon[0], fill="blue")

        roi_id = simpledialog.askstring("ROI ID", "Enter Parking Slot ID:")
        if roi_id:
            self.rois.append({"id": roi_id, "coords": self.current_polygon.copy()})
            print(f"Saved ROI: {roi_id}")
        else:
            print("No ID entered. ROI discarded.")

        self.current_polygon.clear()

    def save_to_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.rois, f, indent=4)
            print(f"Saved {len(self.rois)} ROIs to {file_path}")

if __name__ == "__main__":
    image_path = filedialog.askopenfilename(title="Select Image",
                                            filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if image_path:
        root = tk.Tk()
        app = ROIEditor(root, image_path)
        root.mainloop()
