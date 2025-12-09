import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from PIL import Image, ImageTk
except Exception:
    # If Pillow is not available, show an error when running the script.
    raise ImportError("This script requires the Pillow library. Install via 'pip install pillow'.")


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


class ColorGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Color Image Generator")

        # Main container
        container = ttk.Frame(root, padding=12)
        container.pack(fill="both", expand=True)

        # Size inputs
        size_frame = ttk.Frame(container)
        size_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(size_frame, text="Width:").grid(column=0, row=0, sticky="w")
        self.width_var = tk.StringVar(value="400")
        self.width_entry = ttk.Entry(size_frame, width=8, textvariable=self.width_var)
        self.width_entry.grid(column=1, row=0, sticky="w", padx=(4, 16))

        ttk.Label(size_frame, text="Height:").grid(column=2, row=0, sticky="w")
        self.height_var = tk.StringVar(value="400")
        self.height_entry = ttk.Entry(size_frame, width=8, textvariable=self.height_var)
        self.height_entry.grid(column=3, row=0, sticky="w", padx=(4, 0))

        # Color preview area (regular tk.Frame so bg can be configured)
        self.preview = tk.Frame(container, height=100, bg=rgb_to_hex(0, 0, 0))
        self.preview.pack(fill="x", pady=(0, 8))

        # RGB sliders
        sliders = ttk.Frame(container)
        sliders.pack(fill="x")

        self.r_var = tk.IntVar(value=0)
        self.g_var = tk.IntVar(value=0)
        self.b_var = tk.IntVar(value=0)

        self._make_slider(sliders, "R", self.r_var, 0)
        self._make_slider(sliders, "G", self.g_var, 1)
        self._make_slider(sliders, "B", self.b_var, 2)

        # Generate button
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=(10, 0))

        generate_btn = ttk.Button(btn_frame, text="Generate", command=self.generate_image)
        generate_btn.pack(side="left")

        # Update preview initially
        self.update_preview()

    def _make_slider(self, parent, label, var, col):
        frame = ttk.Frame(parent)
        frame.grid(column=col, row=0, padx=6, sticky="nsew")
        ttk.Label(frame, text=label).pack(anchor="w")
        s = ttk.Scale(frame, from_=0, to=255, orient="horizontal", command=lambda v, vv=var: vv.set(int(float(v))))
        s.pack(fill="x")
        # initialize the slider position to match the variable to avoid an initial jump
        try:
            s.set(var.get())
        except Exception:
            pass
        # Keep scale and var in sync
        var.trace_add("write", lambda *a, v=var: self.update_preview())

    def update_preview(self):
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        hexc = rgb_to_hex(r, g, b)
        # update frame backgrounds
        try:
            self.preview.configure(bg=hexc)
            self.root.configure(bg=hexc)
        except Exception:
            pass

    def generate_image(self):
        # Validate size
        try:
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            if w <= 0 or h <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid size", "Please enter positive integer values for width and height.")
            return

        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()

        img = Image.new("RGB", (w, h), (r, g, b))

        # Show image in a new window
        top = tk.Toplevel(self.root)
        top.title("Generated Image")

        # Convert for display
        tk_img = ImageTk.PhotoImage(img)
        lbl = ttk.Label(top, image=tk_img)
        lbl.image = tk_img  # keep reference
        lbl.pack()

        # Prompt to save automatically
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG image", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("All files", "*")],
                                            initialfile="color_image.png",
                                            title="Save generated image")
        if path:
            try:
                img.save(path)
                messagebox.showinfo("Saved", f"Image saved to: {path}")
            except Exception as e:
                messagebox.showerror("Save error", f"Could not save image:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorGeneratorApp(root)
    root.mainloop()