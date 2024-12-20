import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

class ImageTrimmerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像トリマー")
        self.root.geometry("1300x850")

        # トップボタンフレーム
        self.top_button_frame = tk.Frame(root)
        self.top_button_frame.pack(fill=tk.X, padx=5, pady=5)

        # メインボタン作成
        self.create_main_buttons()

        # メインフレーム
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # 左側フレーム（オリジナル画像とキャンバス）
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # オリジナル画像ラベル
        self.original_label = tk.Label(self.left_frame, text="オリジナル画像")
        self.original_label.pack()

        # 画像表示用キャンバス
        self.canvas = tk.Canvas(self.left_frame, cursor="cross")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 右側フレーム（トリミング履歴と選択画像）
        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # トリミング履歴リストボックス
        self.history_listbox = tk.Listbox(self.right_frame, width=30)
        self.history_listbox.pack(expand=True, fill=tk.BOTH)
        self.history_listbox.bind('<<ListboxSelect>>', self.show_selected_trim)

        # 選択画像ラベル
        self.trim_label = tk.Label(self.right_frame, text="選択したトリミング画像")
        self.trim_label.pack()

        # 選択画像キャンバス
        self.trim_canvas = tk.Canvas(self.right_frame, width=250, height=250)
        self.trim_canvas.pack()

        # トリミング履歴操作ボタン
        self.create_history_buttons()

        # 選択範囲用変数
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.image = None
        self.original_image = None
        
        # トリミング履歴
        self.trim_history = []

        # 複数選択範囲の保持
        self.selected_areas = []
        self.rectangles = []

        # リサイズ設定
        self.resize_width = None
        self.resize_height = None
        self.resize_scale = None

        # メニューバーの作成
        self.create_menu()

        # イベントバインディング
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def create_main_buttons(self):
        # メインボタンを作成
        button_styles = {
            'padx': 10,
            'pady': 5,
            'width': 15
        }

        # 画像を開くボタン
        self.open_btn = tk.Button(
            self.top_button_frame, 
            text="画像を開く", 
            command=self.open_image,
            **button_styles
        )
        self.open_btn.pack(side=tk.LEFT, padx=5)

        # トリミングボタン
        self.trim_btn = tk.Button(
            self.top_button_frame, 
            text="選択範囲をトリミング", 
            command=self.trim_image,
            **button_styles
        )
        self.trim_btn.pack(side=tk.LEFT, padx=5)

        # すべてのトリミングを保存ボタン
        self.save_all_btn = tk.Button(
            self.top_button_frame, 
            text="すべてのトリミングを保存", 
            command=self.save_all_trims,
            **button_styles
        )
        self.save_all_btn.pack(side=tk.LEFT, padx=5)

        # 終了ボタン
        self.exit_btn = tk.Button(
            self.top_button_frame, 
            text="終了", 
            command=self.root.quit,
            **button_styles
        )
        self.exit_btn.pack(side=tk.LEFT, padx=5)

    def create_history_buttons(self):
        # ボタンフレーム
        button_frame = tk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X)

        # 選択したトリミングを削除
        delete_btn = tk.Button(button_frame, text="選択削除", command=self.delete_selected_trim)
        delete_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=2)

        # すべてのトリミングをクリア
        clear_btn = tk.Button(button_frame, text="全削除", command=self.clear_trim_history)
        clear_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="画像を開く", command=self.open_image)
        file_menu.add_command(label="選択範囲をトリミング", command=self.trim_image)
        file_menu.add_command(label="すべてのトリミングを保存", command=self.save_all_trims)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit)

        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="リサイズ幅と高さを指定", command=self.set_resize_dimensions)
        settings_menu.add_command(label="倍率を指定", command=self.set_resize_scale)

    def set_resize_dimensions(self):
        self.resize_width = simpledialog.askinteger("幅を指定", "保存する画像の幅を入力してください", minvalue=1)
        self.resize_height = simpledialog.askinteger("高さを指定", "保存する画像の高さを入力してください", minvalue=1)
        self.resize_scale = None

        if not self.resize_width or not self.resize_height:
            messagebox.showwarning("警告", "有効なサイズを入力してください")

    def set_resize_scale(self):
        self.resize_scale = simpledialog.askfloat("倍率を指定", "保存する画像の倍率を入力してください (例: 0.5 = 50%, 2 = 200%)", minvalue=0.1)
        self.resize_width = None
        self.resize_height = None

        if not self.resize_scale:
            messagebox.showwarning("警告", "有効な倍率を入力してください")

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("画像ファイル", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
            # トリミング履歴をリセット
            self.trim_history = []
            self.history_listbox.delete(0, tk.END)
            # トリミングキャンバスをクリア
            self.trim_canvas.delete("all")
            # 選択範囲をリセット
            self.selected_areas = []
            self.rectangles = []

    def load_image(self, file_path):
        try:
            # 画像を開いてリサイズ
            self.original_image = Image.open(file_path)
            width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
            self.image = self.original_image.copy()
            self.image.thumbnail((width, height), Image.LANCZOS)
            
            # Tkinter互換の画像に変換
            self.tk_image = ImageTk.PhotoImage(self.image)
            
            # キャンバスに画像を表示
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        except Exception as e:
            messagebox.showerror("エラー", f"画像の読み込みに失敗しました: {str(e)}")

    def on_press(self, event):
        # 選択範囲の開始点を記録
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        if self.start_x is None or self.start_y is None:
            return

        # 選択範囲を描画
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, 
            outline="red", width=2
        )

    def on_release(self, event):
        if self.original_image is None or self.image is None:
            messagebox.showwarning("警告", "画像が読み込まれていません")
            return

        if self.start_x is None or self.start_y is None:
            return

        # トリミング範囲を計算
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        # スケール調整
        scale_x = self.original_image.width / self.image.width
        scale_y = self.original_image.height / self.image.height
        
        trim_x1 = int(x1 * scale_x)
        trim_y1 = int(y1 * scale_y)
        trim_x2 = int(x2 * scale_x)
        trim_y2 = int(y2 * scale_y)

        # 選択範囲をリストに追加
        self.selected_areas.append((trim_x1, trim_y1, trim_x2, trim_y2))
        
        # キャンバスに選択範囲を保持
        self.rectangles.append(self.rect)
        self.rect = None

        # 開始点をリセット
        self.start_x = None
        self.start_y = None

    def trim_image(self):
        if not self.selected_areas:
            messagebox.showwarning("警告", "トリミング範囲を選択してください")
            return

        if self.original_image is None:
            messagebox.showwarning("警告", "画像が読み込まれていません")
            return

        try:
            for i, coords in enumerate(self.selected_areas):
                # トリミングを実行
                trimmed_image = self.original_image.crop(coords)
                
                # トリミング名を入力
                trim_name = f"トリミング {len(self.trim_history) + 1}"

                # トリミング履歴に追加
                resize_trim = trimmed_image.copy()
                resize_trim.thumbnail((250, 250), Image.LANCZOS)
                self.trim_history.append({
                    'name': trim_name,
                    'image': trimmed_image,
                    'preview': resize_trim,
                    'coords': coords
                })
                
                # 履歴リストボックスに追加
                self.history_listbox.insert(tk.END, trim_name)
                
            messagebox.showinfo("成功", f"{len(self.selected_areas)}個のトリミングを履歴に追加しました")
            # 選択範囲をリセット
            self.selected_areas = []
            for rect in self.rectangles:
                self.canvas.delete(rect)
            self.rectangles = []
        except Exception as e:
            messagebox.showerror("エラー", f"トリミングに失敗しました: {str(e)}")

    def show_selected_trim(self, event):
        # 選択されたトリミング画像を表示
        try:
            # 選択されたインデックスを取得
            selected_index = self.history_listbox.curselection()[0]
            
            # トリミング画像のプレビューを取得
            preview_image = self.trim_history[selected_index]['preview']
            
            # Tkinter互換の画像に変換
            tk_preview = ImageTk.PhotoImage(preview_image)
            
            # キャンバスをクリアして画像を表示
            self.trim_canvas.delete("all")
            self.trim_canvas.create_image(
                125, 125, 
                anchor=tk.CENTER, 
                image=tk_preview
            )
            
            # 画像への参照を保持（ガベージコレクションを防ぐ）
            self.tk_preview = tk_preview
        except IndexError:
            # 何も選択されていない場合
            self.trim_canvas.delete("all")

    def delete_selected_trim(self):
        # 選択されたトリミングを削除
        try:
            selected_index = self.history_listbox.curselection()[0]
            del self.trim_history[selected_index]
            self.history_listbox.delete(selected_index)
            # キャンバスをクリア
            self.trim_canvas.delete("all")
        except IndexError:
            messagebox.showwarning("警告", "削除する項目を選択してください")

    def clear_trim_history(self):
        # すべてのトリミングを削除
        if messagebox.askyesno("確認", "すべてのトリミングを削除しますか？"):
            self.trim_history.clear()
            self.history_listbox.delete(0, tk.END)
            # キャンバスをクリア
            self.trim_canvas.delete("all")

    def save_all_trims(self):
        if not self.trim_history:
            messagebox.showwarning("警告", "保存するトリミングがありません")
            return

        if self.resize_width is None and self.resize_height is None and self.resize_scale is None:
            messagebox.showwarning("警告", "リサイズする幅、高さ、または倍率を設定してください")
            return

        # 保存ディレクトリを選択
        save_dir = filedialog.askdirectory(title="トリミング画像の保存先を選択")
        
        if save_dir:
            try:
                # 各トリミング画像を保存
                for trim in self.trim_history:
                    if self.resize_scale:
                        # 倍率に基づいてリサイズ
                        new_width = int(trim['image'].width * self.resize_scale)
                        new_height = int(trim['image'].height * self.resize_scale)
                        resized_image = trim['image'].resize((new_width, new_height), Image.LANCZOS)
                    else:
                        # 幅と高さに基づいてリサイズ
                        resized_image = trim['image'].resize((self.resize_width, self.resize_height), Image.LANCZOS)
                    
                    # ファイル名を生成（スペースをアンダースコアに置換）
                    filename = f"{trim['name'].replace(' ', '_')}.png"
                    save_path = os.path.join(save_dir, filename)
                    resized_image.save(save_path)
                
                messagebox.showinfo("成功", f"{len(self.trim_history)}枚の画像を{save_dir}に保存しました")
            except Exception as e:
                messagebox.showerror("エラー", f"画像の保存に失敗しました: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageTrimmerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()