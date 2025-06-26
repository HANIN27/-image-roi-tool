import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
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
        self.current_polygon_drawings = []
        self.saved_drawings = []
        self.rois = []

        self.canvas.bind("<Button-1>", self.add_point)  # Left-click
        self.canvas.bind("<Button-3>", self.undo_last_point)  # Right-click
        self.canvas.bind("<Double-Button-1>", self.complete_polygon)  # Double-click to finish

        self.root.bind("<c>", self.clear_current_polygon)
        self.root.bind("<r>", self.reset_all)
        self.root.bind("<d>", self.delete_roi_by_id)

        save_btn = tk.Button(root, text="💾 Save to JSON", command=self.save_to_json)
        save_btn.pack(pady=10)

        help_text = (
            "Left click = Add point\n"
            "Right click = Undo last point\n"
            "Double click = Finish ROI + enter ID\n"
            "Press 'C' = Clear current polygon\n"
            "Press 'R' = Reset all ROIs\n"
            "Press 'D' = Delete ROI by ID"
        )
        tk.Label(root, text=help_text, justify="left").pack(pady=5)

    def add_point(self, event):
        x, y = event.x, event.y
        self.current_polygon.append([x, y])
        dot = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")
        self.current_polygon_drawings.append(dot)

        if len(self.current_polygon) > 1:
            line = self.canvas.create_line(*self.current_polygon[-2], x, y, fill="blue")
            self.current_polygon_drawings.append(line)

    def undo_last_point(self, event):
        if self.current_polygon:
            self.current_polygon.pop()
            item = self.current_polygon_drawings.pop()
            self.canvas.delete(item)
            if self.current_polygon_drawings:
                # Remove the line too if it was last
                item = self.current_polygon_drawings.pop()
                self.canvas.delete(item)

    def complete_polygon(self, event):
        if len(self.current_polygon) < 3:
            messagebox.showinfo("Invalid", "Polygon needs at least 3 points.")
            return

        # Draw closing line
        line = self.canvas.create_line(*self.current_polygon[-1], *self.current_polygon[0], fill="blue")
        self.current_polygon_drawings.append(line)

        roi_id = simpledialog.askstring("ROI ID", "Enter Parking Slot ID:")
        if roi_id:
            self.rois.append({"id": roi_id, "coords": self.current_polygon.copy()})
            self.saved_drawings.append(self.current_polygon_drawings.copy())
            print(f"Saved ROI: {roi_id}")
        else:
            print("No ID entered. ROI discarded.")
            # Cleanup this polygon from canvas
            for item in self.current_polygon_drawings:
                self.canvas.delete(item)

        self.current_polygon.clear()
        self.current_polygon_drawings.clear()

    def clear_current_polygon(self, event=None):
        for item in self.current_polygon_drawings:
            self.canvas.delete(item)
        self.current_polygon.clear()
        self.current_polygon_drawings.clear()
        print("Cleared current polygon.")

    def reset_all(self, event=None):
        confirm = messagebox.askyesno("Reset", "Delete all saved ROIs?")
        if confirm:
            for drawing in self.saved_drawings:
                for item in drawing:
                    self.canvas.delete(item)
            self.saved_drawings.clear()
            self.rois.clear()
            print("All ROIs deleted.")

    def delete_roi_by_id(self, event=None):
        if not self.rois:
            return

        roi_id = simpledialog.askstring("Delete ROI", "Enter ID to delete:")
        if roi_id:
            for idx, roi in enumerate(self.rois):
                if roi["id"] == roi_id:
                    for item in self.saved_drawings[idx]:
                        self.canvas.delete(item)
                    del self.rois[idx]
                    del self.saved_drawings[idx]
                    print(f"Deleted ROI: {roi_id}")
                    return
            print(f"ROI '{roi_id}' not found.")

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
