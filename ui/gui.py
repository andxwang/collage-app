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
		elif layout_name == '4-vertical':
			self.init_four_vertical()
		elif layout_name == '4-grid':
			self.init_four_grid()
		elif layout_name == '5-2-3':
			self.init_five_two_three()
		elif layout_name == '5-3-2':
			self.init_five_three_two()
	def init_four_vertical(self):
		w, h = self.output_size
		heights = [h//4]*3 + [h - 3*(h//4)]
		y_positions = [0, heights[0], heights[0]+heights[1], heights[0]+heights[1]+heights[2]]
		for i in range(4):
			px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
			tile = Tile(self.canvas, px, py, pw, ph, i, self.check_export)
			self.tiles.append(tile)
		for i in range(3):
			px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
			bar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy, idx=i: self.resize_tiles_vertical(idx, dy, 4))
			self.drag_bars.append(bar)

	def resize_tiles_vertical(self, idx, dy, n):
		prev_h = self.preview_size[1]
		out_h = self.output_size[1]
		scale = out_h / prev_h
		dy_out = int(dy * scale)
		w, h = self.output_size
		heights = [self.tiles[i].h for i in range(n)]
		for i in range(n):
			_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
			heights[i] = ph
		heights[idx] += dy_out
		heights[idx+1] -= dy_out
		min_h = int(50 * scale)
		if heights[idx] < min_h or heights[idx+1] < min_h:
			return
		y_positions = [0]
		for i in range(n-1):
			y_positions.append(y_positions[-1] + heights[i])
		for i in range(n):
			px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
			self.tiles[i].update_size(px, py, pw, ph)
		for i in range(n-1):
			px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
			self.drag_bars[i].update_position(px, py, pw, ph)

	def init_four_grid(self):
		w, h = self.output_size
		# Initial split: 2x2 grid
		widths = [w//2, w - w//2]
		heights = [h//2, h - h//2]
		positions = [
			(0, 0, widths[0], heights[0]),
			(widths[0], 0, widths[1], heights[0]),
			(0, heights[0], widths[0], heights[1]),
			(widths[0], heights[0], widths[1], heights[1])
		]
		for i, (x, y, tw, th) in enumerate(positions):
			px, py, pw, ph = self.scale_coords(x, y, tw, th)
			tile = Tile(self.canvas, px, py, pw, ph, i, self.check_export)
			self.tiles.append(tile)
		# Add vertical and horizontal drag bars
		# Vertical bar
		px, py, pw, ph = self.scale_coords(widths[0]-5, 0, 10, h)
		vbar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dx: self.resize_grid_vertical(dx, widths, heights))
		self.drag_bars.append(vbar)
		# Horizontal bar
		px, py, pw, ph = self.scale_coords(0, heights[0]-5, w, 10)
		hbar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy: self.resize_grid_horizontal(dy, widths, heights, w, h),)
		self.drag_bars.append(hbar)

	def resize_grid_vertical(self, dx, widths, heights):
		prev_w = self.preview_size[0]
		out_w = self.output_size[0]
		scale = out_w / prev_w
		dx_out = int(dx * scale)
		min_w = int(50 * scale)
		widths[0] += dx_out
		widths[1] -= dx_out
		if widths[0] < min_w or widths[1] < min_w:
			return
		w, h = self.output_size
		positions = [
			(0, 0, widths[0], heights[0]),
			(widths[0], 0, widths[1], heights[0]),
			(0, heights[0], widths[0], heights[1]),
			(widths[0], heights[0], widths[1], heights[1])
		]
		for i, (x, y, tw, th) in enumerate(positions):
			px, py, pw, ph = self.scale_coords(x, y, tw, th)
			self.tiles[i].update_size(px, py, pw, ph)
		# Update drag bars
		px, py, pw, ph = self.scale_coords(widths[0]-5, 0, 10, h)
		self.drag_bars[0].update_position(px, py, pw, ph)
		px, py, pw, ph = self.scale_coords(0, heights[0]-5, w, 10)
		self.drag_bars[1].update_position(px, py, pw, ph)

	def resize_grid_horizontal(self, dy, widths, heights, w, h):
		prev_h = self.preview_size[1]
		out_h = self.output_size[1]
		scale = out_h / prev_h
		dy_out = int(dy * scale)
		min_h = int(50 * scale)
		heights[0] += dy_out
		heights[1] -= dy_out
		if heights[0] < min_h or heights[1] < min_h:
			return
		positions = [
			(0, 0, widths[0], heights[0]),
			(widths[0], 0, widths[1], heights[0]),
			(0, heights[0], widths[0], heights[1]),
			(widths[0], heights[0], widths[1], heights[1])
		]
		for i, (x, y, tw, th) in enumerate(positions):
			px, py, pw, ph = self.scale_coords(x, y, tw, th)
			self.tiles[i].update_size(px, py, pw, ph)
		# Update drag bars
		px, py, pw, ph = self.scale_coords(widths[0]-5, 0, 10, h)
		self.drag_bars[0].update_position(px, py, pw, ph)
		px, py, pw, ph = self.scale_coords(0, heights[0]-5, w, 10)
		self.drag_bars[1].update_position(px, py, pw, ph)

	def init_five_two_three(self):
		w, h = self.output_size
		wcol = w // 2
		h_left = [h//2, h - h//2]
		h_right = [h//3, h//3, h - 2*(h//3)]
		# Left column (2 tiles)
		for i in range(2):
			px, py, pw, ph = self.scale_coords(0, sum(h_left[:i]), wcol, h_left[i])
			tile = Tile(self.canvas, px, py, pw, ph, i, self.check_export)
			self.tiles.append(tile)
		# Right column (3 tiles)
		for i in range(3):
			px, py, pw, ph = self.scale_coords(wcol, sum(h_right[:i]), w-wcol, h_right[i])
			tile = Tile(self.canvas, px, py, pw, ph, i+2, self.check_export)
			self.tiles.append(tile)
		# Drag bars for left column (local list)
		self.drag_bars_left = []
		px, py, pw, ph = self.scale_coords(0, h_left[0]-5, wcol, 10)
		bar_left = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy: self.resize_tiles_column(dy, h_left, 2, 0, wcol, 0, 'left'))
		self.drag_bars_left.append(bar_left)
		# Drag bars for right column (local list)
		self.drag_bars_right = []
		for i in range(2):
			px, py, pw, ph = self.scale_coords(wcol, h_right[i]-5+sum(h_right[:i]), w-wcol, 10)
			bar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy, idx=i: self.resize_tiles_column(dy, h_right, 3, 2, w-wcol, idx, 'right'))
			self.drag_bars_right.append(bar)

	def init_five_three_two(self):
		w, h = self.output_size
		wcol = w // 2
		h_left = [h//3, h//3, h - 2*(h//3)]
		h_right = [h//2, h - h//2]
		# Left column (3 tiles)
		for i in range(3):
			px, py, pw, ph = self.scale_coords(0, sum(h_left[:i]), wcol, h_left[i])
			tile = Tile(self.canvas, px, py, pw, ph, i, self.check_export)
			self.tiles.append(tile)
		# Right column (2 tiles)
		for i in range(2):
			px, py, pw, ph = self.scale_coords(wcol, sum(h_right[:i]), w-wcol, h_right[i])
			tile = Tile(self.canvas, px, py, pw, ph, i+3, self.check_export)
			self.tiles.append(tile)
		# Drag bars for left column (local list)
		self.drag_bars_left = []
		for i in range(2):
			px, py, pw, ph = self.scale_coords(0, h_left[i]-5+sum(h_left[:i]), wcol, 10)
			bar = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy, idx=i: self.resize_tiles_column(dy, h_left, 3, 0, wcol, idx, 'left'))
			self.drag_bars_left.append(bar)
		# Drag bar for right column (local list)
		self.drag_bars_right = []
		px, py, pw, ph = self.scale_coords(wcol, h_right[0]-5, w-wcol, 10)
		bar_right = VerticalDragBar(self.canvas, px, py, pw, ph, lambda dy: self.resize_tiles_column(dy, h_right, 2, 3, w-wcol, 0, 'right'))
		self.drag_bars_right.append(bar_right)

	def resize_tiles_column(self, dy, heights, n, tile_offset, col_width, idx=0, which='left'):
		prev_h = self.preview_size[1]
		out_h = self.output_size[1]
		scale = out_h / prev_h
		dy_out = int(dy * scale)
		heights[idx] += dy_out
		heights[idx+1] -= dy_out
		min_h = int(50 * scale)
		if heights[idx] < min_h or heights[idx+1] < min_h:
			return
		y_positions = [0]
		for i in range(n-1):
			y_positions.append(y_positions[-1] + heights[i])
		for i in range(n):
			px, py, pw, ph = self.scale_coords((0 if tile_offset==0 else col_width), y_positions[i], col_width, heights[i])
			self.tiles[tile_offset+i].update_size(px, py, pw, ph)
		# Update drag bars for the correct column only
		if n == 2:
			px, py, pw, ph = self.scale_coords((0 if tile_offset==0 else col_width), heights[0]-5, col_width, 10)
			if which == 'left':
				self.drag_bars_left[0].update_position(px, py, pw, ph)
			else:
				self.drag_bars_right[0].update_position(px, py, pw, ph)
		else:
			for i in range(n-1):
				px, py, pw, ph = self.scale_coords((0 if tile_offset==0 else col_width), heights[i]-5+y_positions[i], col_width, 10)
				if which == 'left':
					self.drag_bars_left[i].update_position(px, py, pw, ph)
				else:
					self.drag_bars_right[i].update_position(px, py, pw, ph)

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
		# Redraw all tiles and drag bars on resize, layout-aware
		w, h = self.output_size
		layout = getattr(self, 'current_layout', None)
		if layout is None:
			# Try to infer layout from tile count
			n = len(self.tiles)
			if n == 3:
				layout = '3-vertical'
			elif n == 4:
				layout = '4-vertical' if len(getattr(self, 'drag_bars', [])) == 3 else '4-grid'
			elif n == 5:
				layout = '5-2-3' if hasattr(self, 'drag_bars_left') else '5-3-2'
			else:
				return
		if layout == '3-vertical':
			heights = [self.tiles[i].h for i in range(3)]
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
		elif layout == '4-vertical':
			n = 4
			heights = [self.tiles[i].h for i in range(n)]
			for i in range(n):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
				heights[i] = ph
			y_positions = [0]
			for i in range(n-1):
				y_positions.append(y_positions[-1] + heights[i])
			for i in range(n):
				px, py, pw, ph = self.scale_coords(0, y_positions[i], w, heights[i])
				self.tiles[i].update_size(px, py, pw, ph)
			for i in range(n-1):
				px, py, pw, ph = self.scale_coords(0, y_positions[i]+heights[i]-5, w, 10)
				self.drag_bars[i].update_position(px, py, pw, ph)
		elif layout == '4-grid':
			# 2x2 grid
			widths = [self.tiles[0].w, self.tiles[1].w]
			heights = [self.tiles[0].h, self.tiles[2].h]
			for i in range(2):
				_, _, pw, _ = self.inv_scale_coords(0, 0, self.tiles[i].w, 0)
				widths[i] = pw
			for i in range(2):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i*2].h)
				heights[i] = ph
			positions = [
				(0, 0, widths[0], heights[0]),
				(widths[0], 0, widths[1], heights[0]),
				(0, heights[0], widths[0], heights[1]),
				(widths[0], heights[0], widths[1], heights[1])
			]
			for i, (x, y, tw, th) in enumerate(positions):
				px, py, pw, ph = self.scale_coords(x, y, tw, th)
				self.tiles[i].update_size(px, py, pw, ph)
			# Drag bars: 0 = vertical, 1 = horizontal
			px, py, pw, ph = self.scale_coords(widths[0]-5, 0, 10, h)
			self.drag_bars[0].update_position(px, py, pw, ph)
			px, py, pw, ph = self.scale_coords(0, heights[0]-5, w, 10)
			self.drag_bars[1].update_position(px, py, pw, ph)
		elif layout == '5-2-3':
			wcol = w // 2
			h_left = [self.tiles[0].h, self.tiles[1].h]
			h_right = [self.tiles[2].h, self.tiles[3].h, self.tiles[4].h]
			for i in range(2):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
				h_left[i] = ph
			for i in range(3):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i+2].h)
				h_right[i] = ph
			# Left column
			y_left = [0, h_left[0]]
			for i in range(2):
				px, py, pw, ph = self.scale_coords(0, (0 if i==0 else y_left[i-1]), wcol, h_left[i])
				self.tiles[i].update_size(px, py, pw, ph)
			# Right column
			y_right = [0, h_right[0], h_right[0]+h_right[1]]
			for i in range(3):
				px, py, pw, ph = self.scale_coords(wcol, y_right[i], w-wcol, h_right[i])
				self.tiles[i+2].update_size(px, py, pw, ph)
			# Drag bars
			# Left
			px, py, pw, ph = self.scale_coords(0, h_left[0]-5, wcol, 10)
			self.drag_bars_left[0].update_position(px, py, pw, ph)
			# Right
			for i in range(2):
				px, py, pw, ph = self.scale_coords(wcol, h_right[i]-5+sum(h_right[:i]), w-wcol, 10)
				self.drag_bars_right[i].update_position(px, py, pw, ph)
		elif layout == '5-3-2':
			wcol = w // 2
			h_left = [self.tiles[0].h, self.tiles[1].h, self.tiles[2].h]
			h_right = [self.tiles[3].h, self.tiles[4].h]
			for i in range(3):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i].h)
				h_left[i] = ph
			for i in range(2):
				_, _, _, ph = self.inv_scale_coords(0, 0, 0, self.tiles[i+3].h)
				h_right[i] = ph
			# Left column
			y_left = [0]
			for i in range(2):
				y_left.append(y_left[-1] + h_left[i])
			for i in range(3):
				px, py, pw, ph = self.scale_coords(0, y_left[i], wcol, h_left[i])
				self.tiles[i].update_size(px, py, pw, ph)
			# Right column
			y_right = [0, h_right[0]]
			for i in range(2):
				px, py, pw, ph = self.scale_coords(wcol, y_right[i], w-wcol, h_right[i])
				self.tiles[i+3].update_size(px, py, pw, ph)
			# Drag bars
			for i in range(2):
				px, py, pw, ph = self.scale_coords(0, h_left[i]-5+y_left[i], wcol, 10)
				self.drag_bars_left[i].update_position(px, py, pw, ph)
			px, py, pw, ph = self.scale_coords(wcol, h_right[0]-5, w-wcol, 10)
			self.drag_bars_right[0].update_position(px, py, pw, ph)

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
		layouts = ['3-vertical', '4-vertical', '4-grid', '5-2-3', '5-3-2']
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
