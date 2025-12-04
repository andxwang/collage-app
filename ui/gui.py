import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from collage.renderer import compose_collage
from config import DEFAULT_OUTPUT_SIZE

class Tile:
	def __init__(self, master, x, y, w, h, idx, on_image_import):
		self.master = master
		self.x, self.y, self.w, self.h = x, y, w, h
		self.idx = idx
		self.image_path = None
		self.on_image_import = on_image_import
		self.frame = tk.Frame(master, width=w, height=h, bg='#ddd', highlightbackground='#888', highlightthickness=1)
		self.frame.place(x=x, y=y, width=w, height=h)
		self.frame.bind('<Button-1>', self.import_image)
		self.label = tk.Label(self.frame, text=f'Tile {idx+1}', bg='#ddd')
		self.label.pack(expand=True, fill='both')
		self.label.bind('<Button-1>', self.import_image)
		self.img_label = None

	def import_image(self, event=None):
		path = filedialog.askopenfilename(filetypes=[('Image Files', '*.jpg *.jpeg *.png *.bmp')])
		if path:
			self.image_path = path
			img = Image.open(path)
			img = img.resize((self.w, self.h), Image.Resampling.LANCZOS)
			img_tk = ImageTk.PhotoImage(img)
			if self.img_label:
				self.img_label.destroy()
			self.img_label = tk.Label(self.frame, image=img_tk)
			self.img_label.image = img_tk
			self.img_label.pack(expand=True, fill='both')
			self.img_label.bind('<Button-1>', self.import_image)
			self.label.pack_forget()
			self.on_image_import()

	def update_size(self, x, y, w, h):
		self.x, self.y, self.w, self.h = x, y, w, h
		self.frame.place(x=x, y=y, width=w, height=h)
		if self.image_path:
			img = Image.open(self.image_path)
			img = img.resize((w, h), Image.Resampling.LANCZOS)
			img_tk = ImageTk.PhotoImage(img)
			self.img_label.configure(image=img_tk)
			self.img_label.image = img_tk

class VerticalDragBar:
	def __init__(self, master, x, y, w, h, on_drag):
		self.master = master
		self.x, self.y, self.w, self.h = x, y, w, h
		self.on_drag = on_drag
		self.bar = tk.Frame(master, bg='#444', cursor='sb_v_double_arrow')
		self.bar.place(x=x, y=y, width=w, height=h)
		self.bar.bind('<B1-Motion>', self.drag)
		self.bar.bind('<Button-1>', self.start_drag)
		self.start_y = None

	def start_drag(self, event):
		self.start_y = event.y_root

	def drag(self, event):
		if self.start_y is not None:
			dy = event.y_root - self.start_y
			self.on_drag(dy)
			self.start_y = event.y_root

	def update_position(self, x, y, w, h):
		self.x, self.y, self.w, self.h = x, y, w, h
		self.bar.place(x=x, y=y, width=w, height=h)

class CollageWindow(tk.Toplevel):
	def __init__(self, master, layout_name, output_size):
		super().__init__(master)
		self.title(f'Collage - {layout_name}')
		self.output_size = output_size
		self.aspect_ratio = output_size[0] / output_size[1]
		# Determine initial preview size (fit to screen, keep aspect)
		screen_w = self.winfo_screenwidth() - 100
		screen_h = self.winfo_screenheight() - 200
		scale_w = min(screen_w, int(screen_h * self.aspect_ratio))
		scale_h = min(screen_h, int(screen_w / self.aspect_ratio))
		self.preview_size = (scale_w, scale_h)
		self.geometry(f'{scale_w}x{scale_h+40}')
		self.resizable(True, True)
		self.canvas = tk.Canvas(self, width=scale_w, height=scale_h, bg='#bbb', highlightthickness=0)
		self.canvas.pack(fill='both', expand=True)
		self.tiles = []
		self.drag_bars = []
		self.images_imported = 0
		self.export_btn = tk.Button(self, text='Export', state='disabled', command=self.export_collage)
		self.export_btn.pack(side='bottom', fill='x')
		self.bind('<Configure>', self.on_resize)
		self.init_layout(layout_name)

	def on_resize(self, event):
		# Keep aspect ratio for canvas
		if event.widget == self:
			w, h = event.width, event.height-40
			aspect = self.aspect_ratio
			if w/h > aspect:
				w = int(h * aspect)
			else:
				h = int(w / aspect)
			self.canvas.config(width=w, height=h)
			self.preview_size = (w, h)
			self.redraw_tiles()

	def scale_coords(self, x, y, w, h):
		# Map output size to preview size
		out_w, out_h = self.output_size
		prev_w, prev_h = self.preview_size
		sx = prev_w / out_w
		sy = prev_h / out_h
		return int(x * sx), int(y * sy), int(w * sx), int(h * sy)

	def inv_scale_coords(self, x, y, w, h):
		# Map preview size to output size
		out_w, out_h = self.output_size
		prev_w, prev_h = self.preview_size
		sx = out_w / prev_w
		sy = out_h / prev_h
		return int(x * sx), int(y * sy), int(w * sx), int(h * sy)

	def init_layout(self, layout_name):
		if layout_name == '3-vertical':
			self.init_three_vertical()
		# Future: elif layout_name == ...

	def init_three_vertical(self):
		w, h = self.output_size
		# Initial heights: equal split
		heights = [h//3, h//3, h - 2*(h//3)]
		y_positions = [0, heights[0], heights[0]+heights[1]]
		for i in range(3):
			# Use preview coordinates
			px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
			tile = Tile(self.canvas, px, py, pw, ph, i, self.check_export)
			self.tiles.append(tile)
		# Add drag bars between tiles
		for i in range(2):
			px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
			bar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy, idx=i: self.resize_tiles(idx, dy))
			self.drag_bars.append(bar)

	def resize_tiles(self, idx, dy):
		# idx: drag bar between tile idx and idx+1
		# Convert dy from preview to output size
		prev_h = self.preview_size[1]
		out_h = self.output_size[1]
		scale = out_h / prev_h
		dy_out = int(dy * scale)
		w, h = self.output_size
		heights = [self.tiles[i].h for i in range(3)]
		# Map preview heights to output heights
		for i in range(3):
			_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
			heights[i] = ph
		heights[idx] += dy_out
		heights[idx+1] -= dy_out
		min_h = int(50 * scale)
		if heights[idx] < min_h or heights[idx+1] < min_h:
			return
		y_positions = [0, heights[0], heights[0]+heights[1]]
		for i in range(3):
			px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
			self.tiles[i].update_size(px, py, pw, ph)
		for i in range(2):
			px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
			self.drag_bars[i].update_position(px, py, pw, ph)
	def redraw_tiles(self):
		# Redraw all tiles and drag bars on resize
		w, h = self.output_size
		heights = [self.tiles[i].h for i in range(3)]
		# Map preview heights to output heights
		for i in range(3):
			_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
			heights[i] = ph
		y_positions = [0, heights[0], heights[0]+heights[1]]
		for i in range(3):
			px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
			self.tiles[i].update_size(px, py, pw, ph)
		for i in range(2):
			px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
			self.drag_bars[i].update_position(px, py, pw, ph)

	def check_export(self):
		self.images_imported = sum(1 for tile in self.tiles if tile.image_path)
		if self.images_imported == len(self.tiles):
			self.export_btn.config(state='normal')
		else:
			self.export_btn.config(state='disabled')

	def export_collage(self):
		image_paths = [tile.image_path for tile in self.tiles]
		# Map preview tile positions to output positions
		positions = []
		for tile in self.tiles:
			x, y, w, h = tile.x, tile.y, tile.w, tile.h
			ox, oy, ow, oh = self.inv_scale_coords(x, y, w, h)
			positions.append((ox, oy, ow, oh))
		collage = compose_collage(image_paths, positions, self.output_size)
		path = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG', '*.jpg')])
		if path:
			collage.save(path)
			messagebox.showinfo('Export', f'Collage saved to {path}')

class LayoutSelector(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Choose Collage Layout')
		self.geometry('400x300')
		self.selected_layout = tk.StringVar()
		layouts = ['3-vertical'] # Future: add more
		for i, layout in enumerate(layouts):
			btn = tk.Radiobutton(self, text=layout, variable=self.selected_layout, value=layout)
			btn.pack(anchor='w', padx=20, pady=10)
		# Add size entry
		size_frame = tk.Frame(self)
		size_frame.pack(pady=10)
		tk.Label(size_frame, text='Collage Size (WxH):').pack(side='left')
		self.size_entry = tk.Entry(size_frame)
		self.size_entry.insert(0, f'{DEFAULT_OUTPUT_SIZE[0]}x{DEFAULT_OUTPUT_SIZE[1]}')
		self.size_entry.pack(side='left')
		start_btn = tk.Button(self, text='Start', command=self.start_collage)
		start_btn.pack(pady=20)

	def start_collage(self):
		layout = self.selected_layout.get()
		if not layout:
			messagebox.showwarning('Select Layout', 'Please select a layout.')
			return
		# Parse size
		size_str = self.size_entry.get()
		try:
			w, h = map(int, size_str.lower().split('x'))
			output_size = (w, h)
		except Exception:
			messagebox.showwarning('Invalid Size', 'Please enter size as WxH, e.g. 1080x1920')
			return
		CollageWindow(self, layout, output_size)

if __name__ == '__main__':
	LayoutSelector().mainloop()
