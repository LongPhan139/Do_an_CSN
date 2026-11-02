import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
import json
import os

# ========== KHAI BÁO BIẾN TOÀN CỤC ==========
secret_digits = []
attempts_left = 10
game_history = []
current_game = {"id": 0, "secret": "", "guesses": []}
current_guess = ""
game_id_counter = 1
computer_possible_numbers = []
cheating_detected = False
invalid_hint_count = 0
player_rankings = []  # Danh sách xếp hạng

# ========== BIẾN THỜI GIAN ==========
game_start_time = None  # Thời gian bắt đầu game
game_total_time = 0     # Tổng thời gian chơi (tính bằng giây)

# ========== ĐỊNH NGHĨA MÀU SẮC ==========
COLORS = {
    # Màu nền chính
    "bg_primary": "#0a192f",        
    "bg_secondary": "#112240",      
    "bg_card": "#1e293b",           
    
    # Màu chữ
    "text_primary": "#e6f1ff",     
    "text_secondary": "#8892b0",    
    "text_accent": "#64ffda",       
    
    # Màu nút
    "btn_primary": "#1d4ed8",       
    "btn_success": "#059669",       
    "btn_danger": "#dc2626",       
    "btn_warning": "#d97706",       
    "btn_info": "#7c3aed",          
    
    # Màu chế độ
    "player": "#3b82f6",           
    "computer": "#8b5cf6",      
    
    # Màu đặc biệt
    "accent_green": "#10b981",    
    "accent_blue": "#3b82f6",     
    "accent_yellow": "#f59e0b",     
    "accent_red": "#ef4444",        
    "accent_purple": "#8b5cf6",     
    
    # Màu viền
    "border": "#2d3748",            
    "border_light": "#4b5563",      #
}

# ========== HÀM THỜI GIAN ==========
def start_game_timer():
    """Bắt đầu tính thời gian cho toàn bộ game"""
    global game_start_time
    game_start_time = datetime.now()

def stop_game_timer():
    """Dừng tính thời gian và trả về tổng thời gian chơi"""
    global game_total_time, game_start_time
    if game_start_time:
        elapsed = datetime.now() - game_start_time
        game_total_time = elapsed.total_seconds()
        game_start_time = None
    return game_total_time

def get_current_game_time():
    """Lấy thời gian hiện tại của game đang chơi"""
    if game_start_time:
        elapsed = datetime.now() - game_start_time
        return elapsed.total_seconds()
    return game_total_time

def format_time(seconds):
    """Định dạng thời gian từ giây sang phút:giây"""
    if seconds < 0:
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# ========== HÀM LƯU VÀ TẢI DỮ LIỆU ==========
def load_data():
    """Tải dữ liệu từ file"""
    global game_history, game_id_counter, player_rankings
    
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Tải lịch sử chơi
    history_file = "data/bagels_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                game_history = data.get("game_history", [])
                game_id_counter = data.get("game_id_counter", 1)
                player_rankings = data.get("player_rankings", [])
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")
            game_history = []
            game_id_counter = 1
            player_rankings = []
    else:
        game_history = []
        game_id_counter = 1
        player_rankings = []

def save_data():
    """Lưu dữ liệu vào file"""
    data = {
        "game_history": game_history[-100:], 
        "game_id_counter": game_id_counter,
        "player_rankings": player_rankings[:50]  #
    }
    
    try:
        with open("data/bagels_history.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi lưu dữ liệu: {e}")

# ========== HÀM XÓA BẢNG XẾP HẠNG ==========
def clear_rankings():
    """Xóa toàn bộ bảng xếp hạng"""
    global player_rankings
    
    # Xác nhận trước khi xóa
    confirm = messagebox.askyesno("Xác nhận", 
                                 "Bạn có chắc chắn muốn xóa TOÀN BỘ bảng xếp hạng?\nHành động này không thể hoàn tác!")
    
    if confirm:
        player_rankings = []  
        save_data()  
        show_rankings()  
        messagebox.showinfo("Thành công", "Đã xóa toàn bộ bảng xếp hạng!")

# ========== HÀM THÊM VÀO XẾP HẠNG ==========
def add_to_rankings(game_entry):
    """Thêm người chơi vào bảng xếp hạng"""
    # Chỉ thêm nếu là chế độ người chơi và THẮNG
    if game_entry["mode"] != "NGƯỜI CHƠI":
        return
    
    # Kiểm tra xem có phải là thắng không
    result = game_entry.get("result", "")
    if "THẮNG" not in result and "THẮNG CUỘC" not in result and "CHÍNH XÁC" not in result:
        return
    
    # Tìm số lượt từ result
    try:
        if "Sau" in result:
            words = result.split()
            for word in words:
                if word.isdigit():
                    turns = int(word)
                    break
            else:
                turns = 10  # Mặc định nếu không tìm thấy
        else:
            turns = 10  # Mặc định nếu không có thông tin
    except:
        turns = 10
    
    score = (11 - turns) * 1000
    
    # Lấy tổng thời gian chơi
    total_time = game_entry.get('total_time', 0)
    
    # Lấy thời gian
    timestamp = game_entry.get("timestamp", "")
    if timestamp:
        try:
            play_time = datetime.strptime(timestamp, "%H:%M:%S %d/%m/%Y").strftime("%d/%m/%Y")
        except:
            play_time = datetime.now().strftime("%d/%m/%Y")
    else:
        play_time = datetime.now().strftime("%d/%m/%Y")
    
    player_entry = {
        "rank": 0,
        "score": score,
        "turns": turns,
        "date": play_time,
        "secret": game_entry["secret"],
        "attempts": len(game_entry["guesses"]),
        "total_time": total_time,
        "time_str": format_time(total_time),
        "timestamp": timestamp 
    }
    
    # Thêm vào danh sách
    player_rankings.append(player_entry)
    
    player_rankings.sort(key=lambda x: (x["score"], -x.get("total_time", 0)), reverse=True)
    
    for i, entry in enumerate(player_rankings[:50]):
        entry["rank"] = i + 1
    
    # Lưu lại
    save_data()
    
    print(f"Đã thêm vào bảng xếp hạng: Điểm {score}, Lượt {turns}, Thời gian {format_time(total_time)}")

# ========== HÀM CHUYỂN TRANG ==========
def show_page(page):
    for frame in [home_frame, player_frame, computer_frame, rules_frame, 
                  history_frame, computer_setup_frame, rankings_frame]:
        frame.pack_forget()
    page.pack(fill=tk.BOTH, expand=True, pady=20)

# ========== HÀM LƯU KẾT QUẢ GAME ==========
def save_game_result(result, reason=""):
    global game_id_counter
    
    # Dừng đồng hồ và lấy tổng thời gian
    total_time = stop_game_timer()
    
    game_entry = {
        "id": game_id_counter,
        "secret": current_game["secret"],
        "guesses": current_game["guesses"][:],
        "result": result,
        "reason": reason,
        "timestamp": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        "mode": "NGƯỜI CHƠI" if game_mode.get() == "player" else "MÁY CHƠI",
        "total_time": total_time
    }
    
    game_history.insert(0, game_entry)
    game_id_counter += 1
    
    print(f"Game kết thúc: {result}, Mode: {game_entry['mode']}")
    
    # Nếu là người chơi thắng, thêm vào xếp hạng
    if game_entry["mode"] == "NGƯỜI CHƠI" and ("THẮNG" in result or "CHÍNH XÁC" in result):
        print("Thêm vào bảng xếp hạng...")
        add_to_rankings(game_entry)
    
    # Lưu vào file
    save_data()
    
    # Ghi log
    log_game(game_entry)

# ========== HÀM GHI LOG ==========
def log_game(game_entry):
    try:
        with open("data/bagels_game_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== Lần chơi #{game_entry['id']} - {game_entry['timestamp']} ===\n")
            f.write(f"Chế độ: {game_entry['mode']}\n")
            f.write(f"Số bí mật: {game_entry['secret']}\n")
            f.write(f"Kết quả: {game_entry['result']}\n")
            
            if 'total_time' in game_entry:
                f.write(f"Tổng thời gian chơi: {format_time(game_entry['total_time'])}\n")
            
            if game_entry.get('reason'):
                f.write(f"Lý do: {game_entry['reason']}\n")
            
            f.write("Lịch sử đoán:\n")
            for i, guess in enumerate(game_entry['guesses'], 1):
                f.write(f"  Lượt {i}: {guess['guess']} → {guess['hint']}\n")
            f.write("="*50 + "\n")
    except Exception as e:
        print(f"Lỗi ghi log: {e}")

# ========== HÀM TẠO SỐ BÍ MẬT ==========
def generate_secret():
    digits = list(range(10))
    random.shuffle(digits)
    return digits[:3]

# ========== HÀM KIỂM TRA ĐOÁN ==========
def check_guess(guess, secret):
    if guess == ''.join(map(str, secret)):
        return "🎉 CHÍNH XÁC! 🎉", "Bạn đã đoán đúng số!"
    
    hints = []
    for i in range(3):
        if guess[i] == str(secret[i]):
            hints.append("Fermi")
        elif guess[i] in map(str, secret):
            hints.append("Pico")
    
    if not hints:
        return "Bagels", "Không có chữ số nào đúng"
    else:
        hints.sort()
        return ' '.join(hints), f"Có {len(hints)} gợi ý"

# ========== HÀM KIỂM TRA GIAN LẬN ==========
def detect_cheating(guess, hint, previous_guesses, possible_numbers=None):
    global invalid_hint_count
    
    # Luật 1: Gợi ý không hợp lệ về mặt toán học
    if hint != "🎉 CHÍNH XÁC! 🎉" and hint != "Bagels":
        fermi_count = hint.count("Fermi")
        pico_count = hint.count("Pico")
        total_hints = fermi_count + pico_count
        
        if total_hints > 3:
            invalid_hint_count += 1
            return False, f"Tổng số gợi ý ({total_hints}) không thể lớn hơn 3"
    
    # Luật 2: Kiểm tra tính nhất quán với các lần đoán trước
    for prev_guess in previous_guesses:
        prev_guess_num = prev_guess['guess']
        prev_hint = prev_guess['hint']
        
        if guess == prev_guess_num and hint != prev_hint:
            invalid_hint_count += 1
            return False, f"Gợi ý không nhất quán: số {guess} trước đây nhận được '{prev_hint}'"
    
    # Luật 3: Kiểm tra với danh sách số có thể
    if possible_numbers:
        possible_after_hint = []
        for number in possible_numbers:
            test_hint, _ = check_guess(guess, list(map(int, number)))
            if test_hint == hint:
                possible_after_hint.append(number)
        
        if len(possible_after_hint) == 0:
            invalid_hint_count += 1
            return False, "Gợi ý này khiến không còn số nào hợp lệ"
    
    # Luật 4: Kiểm tra gợi ý "Chính xác"
    if hint == "🎉 CHÍNH XÁC! 🎉":
        if len(set(guess)) != 3 or not guess.isdigit() or len(guess) != 3:
            invalid_hint_count += 1
            return False, "Số đoán không hợp lệ khi báo 'Chính xác'"
    
    # Reset counter nếu gợi ý hợp lệ
    invalid_hint_count = 0
    return True, "Gợi ý hợp lệ"

# ========== HÀM HIỂN THỊ LỊCH SỬ TRONG GAME ==========
def show_game_history():
    for widget in history_container.winfo_children():
        widget.destroy()
    
    if not game_history:
        tk.Label(history_container, text="Chưa có lịch sử chơi nào!", 
                 font=("Arial", 11), bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(pady=20)
        return
    
    # Tạo scrollable frame
    scroll_frame = tk.Frame(history_container, bg=COLORS["bg_primary"])
    scroll_frame.pack(fill=tk.BOTH, expand=True)
    
    # Tạo Canvas để cuộn
    canvas = tk.Canvas(scroll_frame, bg=COLORS["bg_primary"], highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Thêm thanh cuộn
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Tạo frame bên trong canvas
    inner_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    
    # Cấu hình cuộn chuột
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Gắn sự kiện
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    inner_frame.bind("<Configure>", _on_frame_configure)
    
    # Tạo container chính
    main_container = tk.Frame(inner_frame, bg=COLORS["bg_primary"])
    main_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=5)
    
    # Container cho danh sách lịch sử
    history_list_frame = tk.Frame(main_container, bg=COLORS["bg_primary"])
    history_list_frame.pack(fill=tk.BOTH, expand=True)
    
    # Hiển thị lịch sử
    for game in game_history[:30]:
        game_frame = tk.Frame(history_list_frame, bg=COLORS["bg_card"], relief=tk.RAISED, bd=1)
        game_frame.pack(fill=tk.X, pady=8, ipady=8)
        
        # Header
        header_frame = tk.Frame(game_frame, bg=COLORS["btn_primary"])
        header_frame.pack(fill=tk.X, ipady=4, padx=1, pady=(1, 0))
        
        tk.Label(header_frame, text=f"Lần chơi #{game['id']} - {game['timestamp']}", 
                 font=("Arial", 10, "bold"), bg=COLORS["btn_primary"], 
                 fg="white").pack(side=tk.LEFT, padx=10)
        
        mode_color = COLORS["player"] if game['mode'] == "NGƯỜI CHƠI" else COLORS["computer"]
        tk.Label(header_frame, text=game['mode'], 
                 font=("Arial", 10, "bold"), bg=mode_color, 
                 fg="white", padx=10, pady=2).pack(side=tk.RIGHT, padx=5)
        
        # Nội dung
        content_frame = tk.Frame(game_frame, bg=COLORS["bg_card"])
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Dòng 1: Số bí mật và Kết quả
        top_info_frame = tk.Frame(content_frame, bg=COLORS["bg_card"])
        top_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Số bí mật
        secret_frame = tk.Frame(top_info_frame, bg=COLORS["bg_card"])
        secret_frame.pack(side=tk.LEFT)
        tk.Label(secret_frame, text="Số bí mật: ", 
                 font=("Arial", 10), bg=COLORS["bg_card"], 
                 fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
        tk.Label(secret_frame, text=f"{game['secret']}", 
                 font=("Courier", 11, "bold"), bg=COLORS["bg_card"], 
                 fg=COLORS["text_accent"]).pack(side=tk.LEFT, padx=5)
        
        # Kết quả
        result_frame = tk.Frame(top_info_frame, bg=COLORS["bg_card"])
        result_frame.pack(side=tk.RIGHT)
        tk.Label(result_frame, text="Kết quả: ", 
                 font=("Arial", 10), bg=COLORS["bg_card"], 
                 fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
        
        if "NGƯỜI THẮNG" in game['result'] or "THUA" in game['result']:
            result_color = COLORS["accent_red"]
        elif "MÁY THẮNG" in game['result'] or "THẮNG" in game['result'] or "CHÍNH XÁC" in game['result']:
            result_color = COLORS["accent_green"]
        else:
            result_color = COLORS["accent_yellow"]
        
        tk.Label(result_frame, text=game['result'], 
                 font=("Arial", 10, "bold"), bg=COLORS["bg_card"], 
                 fg=result_color).pack(side=tk.LEFT, padx=5)
        
        # Dòng 2: Thời gian
        if game.get('total_time'):
            time_frame = tk.Frame(content_frame, bg=COLORS["bg_card"])
            time_frame.pack(fill=tk.X, pady=(0, 10))
            tk.Label(time_frame, text="⏱️ Tổng thời gian: ", 
                     font=("Arial", 10), bg=COLORS["bg_card"], 
                     fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
            tk.Label(time_frame, text=format_time(game['total_time']), 
                     font=("Arial", 10, "bold"), bg=COLORS["bg_card"], 
                     fg=COLORS["accent_blue"]).pack(side=tk.LEFT, padx=5)
        
        # Dòng 3: Lý do
        if game.get('reason'):
            reason_frame = tk.Frame(content_frame, bg=COLORS["bg_card"])
            reason_frame.pack(fill=tk.X, pady=(0, 10))
            tk.Label(reason_frame, text="Lý do: ", 
                     font=("Arial", 10), bg=COLORS["bg_card"], 
                     fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
            tk.Label(reason_frame, text=game['reason'], 
                     font=("Arial", 9, "italic"), bg=COLORS["bg_card"], 
                     fg=COLORS["accent_red"]).pack(side=tk.LEFT, padx=5)
        
        # Dòng 4: Lượt đoán
        if game['guesses']:
            guesses_frame = tk.Frame(content_frame, bg="#2d3748", relief=tk.SUNKEN, bd=1)
            guesses_frame.pack(fill=tk.X, pady=(5, 0))
            
            for i, guess_data in enumerate(game['guesses']):
                guess_text = f"Lượt {i+1}: {guess_data['guess']} → {guess_data['hint']}"
                guess_label = tk.Label(guesses_frame, text=guess_text, 
                         font=("Courier", 9), bg="#2d3748", fg=COLORS["text_primary"],
                         anchor="w")
                guess_label.pack(fill=tk.X, padx=8, pady=1)
            
            total_guesses = len(game['guesses'])
            if total_guesses > 0:
                time_info = f"Tổng: {total_guesses} lượt"
                if game.get('total_time'):
                    time_info += f" - Thời gian: {format_time(game['total_time'])}"
                tk.Label(guesses_frame, text=time_info, 
                         font=("Arial", 8, "italic"), bg="#2d3748", fg=COLORS["text_secondary"],
                         anchor="w").pack(fill=tk.X, padx=8, pady=(2, 1))

    # Điều chỉnh canvas
    def _configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", _configure_canvas)

# ========== HÀM HIỂN THỊ BẢNG XẾP HẠNG ==========
def show_rankings():
    """Hiển thị bảng xếp hạng"""
    show_page(rankings_frame)
    
    # Xóa nội dung cũ
    for widget in rankings_container.winfo_children():
        widget.destroy()
    
    # Tiêu đề
    title_frame = tk.Frame(rankings_container, bg=COLORS["bg_primary"])
    title_frame.pack(fill=tk.X, pady=(0, 15))
    
    tk.Label(title_frame, text="🏆 BẢNG XẾP HẠNG TOP 10", 
             font=("Arial", 16, "bold"), bg=COLORS["bg_primary"], 
             fg=COLORS["text_accent"]).pack()
    
    tk.Label(title_frame, text="(Chỉ tính chế độ Người chơi khi THẮNG)", 
             font=("Arial", 11), bg=COLORS["bg_primary"], 
             fg=COLORS["text_secondary"]).pack(pady=5)
    
    if not player_rankings:
        tk.Label(rankings_container, text="Chưa có bảng xếp hạng nào!\nHãy chơi và thắng ở chế độ Người chơi để lập kỷ lục!", 
                 font=("Arial", 12), bg=COLORS["bg_card"], fg=COLORS["text_secondary"], 
                 justify=tk.CENTER).pack(pady=50, padx=20)
        return
    
    # Tiêu đề cột
    header_frame = tk.Frame(rankings_container, bg=COLORS["btn_primary"], height=40)
    header_frame.pack(fill=tk.X, pady=(0, 5))
    header_frame.pack_propagate(False)
    
    columns = ["Hạng", "Điểm", "Lượt", "Thời gian", "Ngày", "Số bí mật"]
    col_widths = [80, 100, 80, 100, 120, 120]
    
    for i, (col, width) in enumerate(zip(columns, col_widths)):
        tk.Label(header_frame, text=col, font=("Arial", 11, "bold"), 
                bg=COLORS["btn_primary"], fg="white", width=width//10).pack(side=tk.LEFT, padx=2)
    
    # Hiển thị top 10
    for i, player in enumerate(player_rankings[:10]):
        if i % 2 == 0:
            bg_color = COLORS["bg_card"]
        else:
            bg_color = COLORS["bg_secondary"]
        
        row_frame = tk.Frame(rankings_container, bg=bg_color, height=35)
        row_frame.pack(fill=tk.X, pady=1)
        row_frame.pack_propagate(False)
        
        # Hiển thị huy chương cho top 3
        if i == 0:
            rank_text = "🥇 #1"
            rank_color = "#FFD700"  # Vàng
        elif i == 1:
            rank_text = "🥈 #2"
            rank_color = "#C0C0C0"  # Bạc
        elif i == 2:
            rank_text = "🥉 #3"
            rank_color = "#CD7F32"  # Đồng
        else:
            rank_text = f"#{i+1}"
            rank_color = COLORS["text_primary"]
        
        tk.Label(row_frame, text=rank_text, font=("Arial", 10, "bold"), 
                bg=bg_color, fg=rank_color, width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Label(row_frame, text=f"{player['score']:,}", font=("Arial", 10, "bold"), 
                bg=bg_color, fg=COLORS["accent_green"], width=10).pack(side=tk.LEFT, padx=2)
        
        tk.Label(row_frame, text=str(player['turns']), font=("Arial", 10), 
                bg=bg_color, fg=COLORS["text_primary"], width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Label(row_frame, text=player.get('time_str', format_time(player.get('total_time', 0))), 
                font=("Arial", 9), bg=bg_color, fg=COLORS["accent_blue"], width=10).pack(side=tk.LEFT, padx=2)
        
        tk.Label(row_frame, text=player['date'], font=("Arial", 9), 
                bg=bg_color, fg=COLORS["text_secondary"], width=12).pack(side=tk.LEFT, padx=2)
        
        tk.Label(row_frame, text=player['secret'], font=("Courier", 10, "bold"), 
                bg=bg_color, fg=COLORS["text_accent"], width=12).pack(side=tk.LEFT, padx=2)
    
    # Thông tin thống kê
    stats_frame = tk.Frame(rankings_container, bg=COLORS["bg_primary"])
    stats_frame.pack(fill=tk.X, pady=15)
    
    if player_rankings:
        total_players = len(player_rankings)
        avg_score = sum(p['score'] for p in player_rankings[:10]) / min(10, total_players)
        best_time = min(p.get('total_time', 99999) for p in player_rankings[:10])
        
        tk.Label(stats_frame, text=f"📊 Thống kê: {total_players} người chơi | Điểm TB top 10: {avg_score:,.0f} | Thời gian tốt nhất: {format_time(best_time)}", 
                 font=("Arial", 10), bg=COLORS["bg_primary"], fg=COLORS["text_secondary"]).pack()

# ========== HÀM KHỞI TẠO SỐ CHO MÁY ==========
def init_computer_possible_numbers():
    global computer_possible_numbers
    computer_possible_numbers = []
    for i in range(10):
        for j in range(10):
            for k in range(10):
                if i != j and i != k and j != k:
                    computer_possible_numbers.append(f"{i}{j}{k}")

def filter_possible_numbers(guess, hint, possible_numbers):
    filtered = []
    for number in possible_numbers:
        test_hint, _ = check_guess(guess, list(map(int, number)))
        if test_hint == hint:
            filtered.append(number)
    return filtered

def computer_auto_guess():
    global attempts_left, computer_possible_numbers
    
    if not computer_possible_numbers:
        computer_result_label.config(text="⚠️ Không có số nào hợp lệ để đoán!", foreground=COLORS["accent_red"])
        return
    
    guess = computer_possible_numbers[0]
    computer_guess_entry.delete(0, tk.END)
    computer_guess_entry.insert(0, guess)
    
    computer_status_label.config(text="Nhấn nút gợi ý bên dưới để phản hồi", 
                               foreground=COLORS["accent_blue"])
    computer_possible_label.config(text=f"Số khả năng còn: {len(computer_possible_numbers)}")

# ========== HÀM XỬ LÝ GỢI Ý CHO MÁY ==========
def give_hint_to_computer(hint_type):
    global attempts_left, computer_possible_numbers, cheating_detected, invalid_hint_count
    
    guess = computer_guess_entry.get().strip()
    
    if not guess.isdigit() or len(guess) != 3:
        computer_result_label.config(text="⚠️ Số đoán không hợp lệ!", foreground=COLORS["accent_red"])
        return
    
    if len(set(guess)) != 3:
        computer_result_label.config(text="⚠️ 3 chữ số phải khác nhau!", foreground=COLORS["accent_red"])
        return
    
    if attempts_left <= 0:
        computer_result_label.config(text="⛔ Máy đã hết lượt đoán!", foreground=COLORS["accent_red"])
        return
    
    attempts_left -= 1
    
    if hint_type == "correct":
        hint = "🎉 CHÍNH XÁC! 🎉"
        explanation = "Chính xác!"
    elif hint_type == "none":
        hint = "Bagels"
        explanation = "Không có chữ số nào đúng"
    else:
        pico_count = computer_pico_count.get()
        fermi_count = computer_fermi_count.get()
        
        if pico_count == 0 and fermi_count == 0:
            hint = "Bagels"
            explanation = "Không có chữ số nào đúng"
        else:
            hints = []
            hints.extend(["Pico"] * pico_count)
            hints.extend(["Fermi"] * fermi_count)
            hints.sort()
            hint = ' '.join(hints)
            explanation = f"{fermi_count} Fermi, {pico_count} Pico"
    
    # PHÁT HIỆN GIAN LẬN
    is_valid, cheat_reason = detect_cheating(guess, hint, current_game["guesses"], computer_possible_numbers)
    
    if not is_valid:
        current_game["guesses"].append({
            "guess": guess,
            "hint": f"Gợi ý: {hint} - ❌ GIAN LẬN!"
        })
        
        computer_history_text.insert("1.0", f"Lượt {10-attempts_left}: {guess} → ❌ GIAN LẬN!\n")
        computer_history_text.tag_add("cheat", "1.0", "1.end")
        computer_history_text.tag_config("cheat", foreground=COLORS["accent_red"], font=("Courier", 10, "bold"))
        
        computer_result_label.config(text=f"⚠️ PHÁT HIỆN GIAN LẬN: {cheat_reason}", foreground=COLORS["accent_red"])
        
        save_game_result("MÁY THẮNG - Phát hiện gian lận", 
                       f"Gợi ý sai - {cheat_reason}")
        disable_computer_buttons()
        return
    
    # Nếu gợi ý hợp lệ
    current_game["guesses"].append({
        "guess": guess,
        "hint": hint
    })
    
    if hint == "🎉 CHÍNH XÁC! 🎉":
        computer_history_text.insert("1.0", f"Lượt {10-attempts_left}: {guess} → 🎉 CHÍNH XÁC!\n")
        computer_history_text.tag_add("correct", "1.0", "1.end")
        computer_history_text.tag_config("correct", foreground=COLORS["accent_green"], font=("Courier", 10, "bold"))
    else:
        computer_history_text.insert("1.0", f"Lượt {10-attempts_left}: {guess} → {hint}\n")
    
    computer_status_label.config(text=f"Còn lại: {attempts_left} lượt", 
                               foreground=COLORS["accent_red"] if attempts_left < 3 else COLORS["text_secondary"])
    
    computer_possible_numbers = filter_possible_numbers(guess, hint, computer_possible_numbers)
    
    if hint == "🎉 CHÍNH XÁC! 🎉":
        total_time = get_current_game_time()
        computer_result_label.config(text=f"🎉 Máy đoán đúng: {guess}!\n⏱️ Thời gian chơi: {format_time(total_time)}", 
                                   foreground=COLORS["accent_green"])
        save_game_result(f"MÁY THẮNG - Sau {10-attempts_left} lượt")
        disable_computer_buttons()
    elif attempts_left == 0:
        if invalid_hint_count >= 1:
            computer_result_label.config(text=f"🤥 Phát hiện gian lận! Máy thắng!", 
                                       foreground=COLORS["accent_red"])
            save_game_result("MÁY THẮNG - Phát hiện gian lận", 
                           "Gợi ý sai nhiều lần dẫn đến không có số hợp lệ")
        else:
            total_time = get_current_game_time()
            computer_result_label.config(text=f"⏰ Máy hết lượt! Người chơi thắng!\n⏱️ Thời gian chơi: {format_time(total_time)}", 
                                       foreground=COLORS["accent_red"])
            save_game_result("NGƯỜI THẮNG - Máy hết lượt")
        disable_computer_buttons()
    elif not computer_possible_numbers:
        computer_result_label.config(text=f"⚠️ Không có số nào hợp lệ!", 
                                   foreground=COLORS["accent_red"])
        save_game_result("NGƯỜI THẮNG - Máy không thể đoán")
        disable_computer_buttons()
    else:
        computer_result_label.config(text=f"Kết quả: {hint} ({explanation})", 
                                   foreground=COLORS["accent_yellow"] if hint == "Bagels" else COLORS["accent_blue"])
        computer_auto_guess()
    
    computer_pico_count.set(0)
    computer_fermi_count.set(0)
    update_counter_labels()

def disable_computer_buttons():
    computer_auto_btn.config(state=tk.DISABLED)
    computer_hint_none_btn.config(state=tk.DISABLED)
    computer_hint_correct_btn.config(state=tk.DISABLED)
    computer_pico_plus_btn.config(state=tk.DISABLED)
    computer_pico_minus_btn.config(state=tk.DISABLED)
    computer_fermi_plus_btn.config(state=tk.DISABLED)
    computer_fermi_minus_btn.config(state=tk.DISABLED)
    computer_custom_hint_btn.config(state=tk.DISABLED)

def update_counter_labels():
    computer_pico_label.config(text=f"Pico: {computer_pico_count.get()}")
    computer_fermi_label.config(text=f"Fermi: {computer_fermi_count.get()}")

def update_counter(counter_type, delta):
    if counter_type == "pico":
        current = computer_pico_count.get()
        new_value = max(0, min(3, current + delta))
        computer_pico_count.set(new_value)
        
        if new_value <= 0:
            computer_pico_minus_btn.config(state=tk.DISABLED)
        else:
            computer_pico_minus_btn.config(state=tk.NORMAL)
            
        if new_value >= 3:
            computer_pico_plus_btn.config(state=tk.DISABLED)
        else:
            computer_pico_plus_btn.config(state=tk.NORMAL)
            
    else:  # fermi
        current = computer_fermi_count.get()
        new_value = max(0, min(3, current + delta))
        computer_fermi_count.set(new_value)
        
        if new_value <= 0:
            computer_fermi_minus_btn.config(state=tk.DISABLED)
        else:
            computer_fermi_minus_btn.config(state=tk.NORMAL)
            
        if new_value >= 3:
            computer_fermi_plus_btn.config(state=tk.DISABLED)
        else:
            computer_fermi_plus_btn.config(state=tk.NORMAL)
    
    update_counter_labels()
    
    total = computer_pico_count.get() + computer_fermi_count.get()
    if total > 3:
        if computer_pico_count.get() > 0:
            computer_pico_count.set(max(0, computer_pico_count.get() - (total - 3)))
        else:
            computer_fermi_count.set(max(0, computer_fermi_count.get() - (total - 3)))
        
        update_counter_labels()
        update_counter("pico", 0)
        update_counter("fermi", 0)

# ========== HÀM BẮT ĐẦU GAME NGƯỜI CHƠI ==========
def start_player_game():
    global secret_digits, attempts_left, current_guess, current_game, game_mode, game_total_time
    
    game_mode.set("player")
    secret_digits = generate_secret()
    attempts_left = 10
    current_guess = ""
    game_total_time = 0
    
    current_game = {
        "id": game_id_counter,
        "secret": ''.join(map(str, secret_digits)),
        "guesses": [],
        "mode": "NGƯỜI CHƠI"
    }
    
    show_page(player_frame)
    player_info_label.config(text=f"Lần chơi #{game_id_counter} - Chế độ: Người chơi")
    player_status_label.config(text=f"Còn lại: {attempts_left} lượt", foreground=COLORS["text_secondary"])
    player_result_label.config(text="")
    player_history_text.delete("1.0", tk.END)
    player_guess_entry.delete(0, tk.END)
    player_guess_entry.config(state=tk.NORMAL)
    player_guess_btn.config(state=tk.NORMAL)
    player_guess_entry.focus()
    
    player_timer_label.config(text="⏱️ Thời gian: 00:00")
    
    start_game_timer()

# Biến lưu số bí mật của người chơi
player_secret_number = ""

# ========== HÀM BẮT ĐẦU GAME MÁY CHƠI ==========
def start_computer_game():
    global secret_digits, attempts_left, current_guess, current_game, game_mode, cheating_detected, player_secret_number, invalid_hint_count, game_total_time
    
    secret_number = computer_secret_entry.get().strip()
    
    if not secret_number.isdigit() or len(secret_number) != 3:
        messagebox.showerror("Lỗi", "Vui lòng nhập đúng 3 chữ số!")
        computer_secret_entry.focus()
        return
    
    if len(set(secret_number)) != 3:
        messagebox.showerror("Lỗi", "3 chữ số phải khác nhau!")
        computer_secret_entry.focus()
        return
    
    game_mode.set("computer")
    secret_digits = list(map(int, secret_number))
    attempts_left = 10
    current_guess = ""
    cheating_detected = False
    invalid_hint_count = 0
    player_secret_number = secret_number
    game_total_time = 0
    
    current_game = {
        "id": game_id_counter,
        "secret": secret_number,
        "guesses": [],
        "mode": "MÁY CHƠI"
    }
    
    show_page(computer_frame)
    computer_info_label.config(text=f"Lần chơi #{game_id_counter} - Chế độ: Máy chơi")
    computer_status_label.config(text=f"Còn lại: {attempts_left} lượt", foreground=COLORS["text_secondary"])
    computer_result_label.config(text="")
    computer_history_text.delete("1.0", tk.END)
    computer_guess_entry.delete(0, tk.END)
    
    computer_secret_label.config(text=f"Số bạn đang nghĩ là: {player_secret_number}")
    
    computer_pico_count.set(0)
    computer_fermi_count.set(0)
    update_counter_labels()
    
    init_computer_possible_numbers()
    
    computer_auto_btn.config(state=tk.NORMAL)
    computer_hint_none_btn.config(state=tk.NORMAL)
    computer_hint_correct_btn.config(state=tk.NORMAL)
    computer_pico_plus_btn.config(state=tk.NORMAL)
    computer_pico_minus_btn.config(state=tk.DISABLED)
    computer_fermi_plus_btn.config(state=tk.NORMAL)
    computer_fermi_minus_btn.config(state=tk.DISABLED)
    computer_custom_hint_btn.config(state=tk.NORMAL)
    
    start_game_timer()
    computer_auto_guess()

# ========== HÀM XỬ LÝ ĐOÁN (CHẾ ĐỘ NGƯỜI CHƠI) ==========
def make_player_guess():
    global attempts_left, current_guess
    
    guess = player_guess_entry.get().strip()
    
    if not guess.isdigit() or len(guess) != 3:
        player_result_label.config(text="⚠️ Vui lòng nhập đúng 3 chữ số!", foreground=COLORS["accent_red"])
        return
    
    if len(set(guess)) != 3:
        player_result_label.config(text="⚠️ 3 chữ số phải khác nhau!", foreground=COLORS["accent_red"])
        return
    
    if attempts_left <= 0:
        player_result_label.config(text="⛔ Bạn đã hết lượt đoán!", foreground=COLORS["accent_red"])
        return
    
    attempts_left -= 1
    current_guess = guess
    
    hint, explanation = check_guess(guess, secret_digits)
    
    current_game["guesses"].append({
        "guess": guess,
        "hint": hint
    })
    
    player_history_text.insert("1.0", f"Lượt {10-attempts_left}: {guess} → {hint}\n")
    
    player_status_label.config(text=f"Còn lại: {attempts_left} lượt", 
                             foreground=COLORS["accent_red"] if attempts_left < 3 else COLORS["text_secondary"])
    
    if hint == "🎉 CHÍNH XÁC! 🎉":
        total_time = get_current_game_time()
        
        player_result_label.config(
            text=f"🎉 Chúc mừng! Bạn đoán đúng: {guess}!\n⏱️ Thời gian chơi: {format_time(total_time)}", 
            foreground=COLORS["accent_green"]
        )
        save_game_result(f"THẮNG CUỘC - Sau {10-attempts_left} lượt")  # Đổi thành THẮNG CUỘC
        player_guess_btn.config(state=tk.DISABLED)
        player_guess_entry.config(state=tk.DISABLED)
    elif attempts_left == 0:
        total_time = get_current_game_time()
        
        player_result_label.config(
            text=f"⏰ Hết lượt! Số bí mật là: {''.join(map(str, secret_digits))}\n⏱️ Thời gian chơi: {format_time(total_time)}", 
            foreground=COLORS["accent_red"]
        )
        save_game_result(f"THUA CUỘC - Hết lượt")
        player_guess_btn.config(state=tk.DISABLED)
        player_guess_entry.config(state=tk.DISABLED)
    else:
        player_result_label.config(text=f"Kết quả: {hint} ({explanation})", 
                                 foreground=COLORS["accent_yellow"] if hint == "Bagels" else COLORS["accent_blue"])
    
    player_guess_entry.delete(0, tk.END)
    player_guess_entry.focus()

# ========== CÁC HÀM HIỂN THỊ TRANG ==========
def show_rules_page():
    show_page(rules_frame)

def view_history():
    show_game_history()
    show_page(history_frame)

def view_rankings():
    show_rankings()

def go_back_from_history():
    if game_mode.get() == "player":
        show_page(player_frame)
    else:
        show_page(computer_frame)

def go_back_from_rankings():
    show_page(home_frame)

def start_computer_mode():
    show_page(computer_setup_frame)

def start_computer_game_with_same_number():
    global player_secret_number
    
    if not player_secret_number:
        messagebox.showinfo("Thông báo", "Chưa có số bí mật nào. Vui lòng nhập số mới.")
        start_computer_mode()
        return
    
    computer_secret_entry.delete(0, tk.END)
    computer_secret_entry.insert(0, player_secret_number)
    start_computer_game()

# ========== HÀM CẬP NHẬT ĐỒNG HỒ ==========
def update_player_timer():
    if game_mode.get() == "player" and game_start_time:
        elapsed = get_current_game_time()
        player_timer_label.config(text=f"⏱️ Thời gian: {format_time(elapsed)}")
    player_timer_label.after(1000, update_player_timer)

def update_computer_timer():
    if game_mode.get() == "computer" and game_start_time:
        elapsed = get_current_game_time()
        computer_timer_label.config(text=f"⏱️ Thời gian: {format_time(elapsed)}")
    computer_timer_label.after(1000, update_computer_timer)

# ========== KHỞI TẠO GIAO DIỆN ==========
root = tk.Tk()
root.title("Trò Chơi Bagels - Đoán Số Bí Mật")
root.geometry("1000x750")
root.configure(bg=COLORS["bg_primary"])

load_data()

game_mode = tk.StringVar(value="player")
computer_pico_count = tk.IntVar(value=0)
computer_fermi_count = tk.IntVar(value=0)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)

# ===== TRANG CHỦ =====
home_frame = tk.Frame(root, bg=COLORS["bg_primary"])

title_label = tk.Label(home_frame, 
                      text="🔢 Trò Chơi BAGELS",
                      font=("Arial", 32, "bold"),
                      bg=COLORS["bg_primary"],
                      fg=COLORS["text_accent"])
title_label.pack(pady=20)

subtitle_label = tk.Label(home_frame,
                         text="Đoán số bí mật 3 chữ số",
                         font=("Arial", 18),
                         bg=COLORS["bg_primary"],
                         fg=COLORS["text_secondary"])
subtitle_label.pack(pady=5)

btn_container = tk.Frame(home_frame, bg=COLORS["bg_primary"])
btn_container.pack(pady=20)

player_mode_btn = tk.Button(btn_container,
                           text="🎮 Người chơi đoán",
                           font=("Arial", 14, "bold"),
                           bg=COLORS["player"],
                           fg="white",
                           width=20,
                           height=2,
                           relief=tk.FLAT,
                           activebackground=COLORS["accent_blue"],
                           command=start_player_game)
player_mode_btn.pack(pady=8)

computer_mode_btn = tk.Button(btn_container,
                             text="🤖 Máy đoán số",
                             font=("Arial", 14, "bold"),
                             bg=COLORS["computer"],
                             fg="white",
                             width=20,
                             height=2,
                             relief=tk.FLAT,
                             activebackground=COLORS["accent_purple"],
                             command=start_computer_mode)
computer_mode_btn.pack(pady=8)

rankings_btn = tk.Button(btn_container,
                        text="🏆 Bảng xếp hạng",
                        font=("Arial", 14, "bold"),
                        bg="#f59e0b",
                        fg="white",
                        width=20,
                        height=2,
                        relief=tk.FLAT,
                        activebackground="#fbbf24",
                        command=view_rankings)
rankings_btn.pack(pady=8)

rules_btn = tk.Button(btn_container,
                     text="📖 Luật chơi",
                     font=("Arial", 14),
                     bg=COLORS["btn_warning"],
                     fg="white",
                     width=20,
                     height=2,
                     relief=tk.FLAT,
                     activebackground=COLORS["accent_yellow"],
                     command=show_rules_page)
rules_btn.pack(pady=8)

exit_btn = tk.Button(btn_container,
                    text="🚪 Thoát game",
                    font=("Arial", 14),
                    bg=COLORS["btn_danger"],
                    fg="white",
                    width=20,
                    height=2,
                    relief=tk.FLAT,
                    activebackground=COLORS["accent_red"],
                    command=lambda: [save_data(), root.quit()])
exit_btn.pack(pady=8)

# ===== TRANG XẾP HẠNG =====
rankings_frame = tk.Frame(root, bg=COLORS["bg_primary"])

rankings_header = tk.Frame(rankings_frame, bg="#f59e0b", height=70)
rankings_header.pack(fill=tk.X)
rankings_header.pack_propagate(False)

tk.Label(rankings_header, text="🏆 BẢNG XẾP HẠNG TOP PLAYERS", 
         font=("Arial", 18, "bold"), bg="#f59e0b", fg="white").pack(pady=15)

rankings_container = tk.Frame(rankings_frame, bg=COLORS["bg_primary"])
rankings_container.pack(pady=15, padx=30, fill=tk.BOTH, expand=True)

# Frame cho nút điều khiển
rankings_control_frame = tk.Frame(rankings_frame, bg=COLORS["bg_primary"])
rankings_control_frame.pack(pady=10)

tk.Button(rankings_control_frame,
         text="🗑️ Xóa bảng xếp hạng",
         font=("Arial", 11, "bold"),
         bg=COLORS["btn_danger"],
         fg="white",
         relief=tk.FLAT,
         width=18,
         activebackground=COLORS["accent_red"],
         command=clear_rankings).pack(side=tk.LEFT, padx=5)

tk.Button(rankings_control_frame,
         text="🔄 Tải lại",
         font=("Arial", 11),
         bg=COLORS["btn_primary"],
         fg="white",
         relief=tk.FLAT,
         width=12,
         activebackground=COLORS["accent_blue"],
         command=show_rankings).pack(side=tk.LEFT, padx=5)

tk.Button(rankings_control_frame,
         text="🔙 Quay về trang chủ",
         font=("Arial", 11),
         bg=COLORS["btn_info"],
         fg="white",
         relief=tk.FLAT,
         width=18,
         activebackground=COLORS["accent_purple"],
         command=go_back_from_rankings).pack(side=tk.LEFT, padx=5)

# ===== TRANG CÀI ĐẶT CHO MÁY CHƠI =====
computer_setup_frame = tk.Frame(root, bg=COLORS["bg_primary"])

setup_header = tk.Frame(computer_setup_frame, bg=COLORS["computer"], height=70)
setup_header.pack(fill=tk.X)
setup_header.pack_propagate(False)

tk.Label(setup_header, text="🤖 NHẬP SỐ BÍ MẬT CHO MÁY ĐOÁN", 
         font=("Arial", 18, "bold"), bg=COLORS["computer"], fg="white").pack(pady=15)

setup_instructions = tk.Label(computer_setup_frame,
                             text="""Hãy nghĩ một số bí mật 3 chữ số và nhập vào đây.
Sau đó máy sẽ cố gắng đoán số của bạn trong 10 lượt.

📌 Lưu ý:
• 3 chữ số phải khác nhau 
• Không thay đổi số trong khi máy đang đoán
• Cung cấp gợi ý chính xác cho máy
• Hệ thống sẽ TỰ ĐỘNG PHÁT HIỆN GIAN LẬN nếu bạn cung cấp gợi ý sai!""",
                             font=("Arial", 11),
                             bg=COLORS["bg_primary"],
                             fg=COLORS["text_primary"],
                             justify=tk.LEFT,
                             wraplength=550)
setup_instructions.pack(pady=15, padx=25)

setup_input_frame = tk.Frame(computer_setup_frame, bg=COLORS["bg_primary"])
tk.Label(setup_input_frame,
        text=" Nhập số bạn muốn máy đoán (3 chữ số khác nhau):",
        font=("Arial", 12, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_secondary"]).pack(pady=8)

setup_entry_container = tk.Frame(setup_input_frame, bg=COLORS["bg_primary"])
computer_secret_entry = tk.Entry(setup_entry_container,
                               width=10,
                               font=("Arial", 24),
                               justify='center',
                               bg=COLORS["bg_card"],
                               fg=COLORS["text_accent"],
                               relief=tk.SOLID,
                               bd=2,
                               insertbackground=COLORS["text_accent"])
computer_secret_entry.pack(side=tk.LEFT, padx=5)

setup_start_btn = tk.Button(setup_entry_container,
                           text="Bắt đầu chơi",
                           font=("Arial", 12, "bold"),
                           bg=COLORS["btn_success"],
                           fg="white",
                           relief=tk.FLAT,
                           height=1,
                           activebackground=COLORS["accent_green"],
                           command=start_computer_game)
setup_start_btn.pack(side=tk.LEFT, padx=5)
setup_entry_container.pack()
setup_input_frame.pack(pady=15)

setup_nav_frame = tk.Frame(computer_setup_frame, bg=COLORS["bg_primary"])
tk.Button(setup_nav_frame,
         text="🏠 Trang chủ",
         font=("Arial", 11),
         bg=COLORS["btn_primary"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_blue"],
         command=lambda: show_page(home_frame)).pack(side=tk.LEFT, padx=8)

tk.Button(setup_nav_frame,
         text="🔙 Quay lại",
         font=("Arial", 11),
         bg=COLORS["btn_info"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_purple"],
         command=lambda: show_page(home_frame)).pack(side=tk.LEFT, padx=8)

setup_nav_frame.pack(pady=20)

# ===== TRANG CHẾ ĐỘ NGƯỜI CHƠI =====
player_frame = tk.Frame(root, bg=COLORS["bg_primary"])

player_header = tk.Frame(player_frame, bg=COLORS["player"], height=70)
player_header.pack(fill=tk.X)
player_header.pack_propagate(False)

tk.Label(player_header, text="🎮 CHẾ ĐỘ NGƯỜI CHƠI", 
         font=("Arial", 18, "bold"), bg=COLORS["player"], fg="white").pack(pady=15)

player_info_label = tk.Label(player_frame,
                           text="",
                           font=("Arial", 12),
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_primary"])
player_info_label.pack(pady=8)

player_status_label = tk.Label(player_frame,
                              text="",
                              font=("Arial", 12, "bold"),
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_secondary"])
player_status_label.pack(pady=3)

player_timer_label = tk.Label(player_frame,
                             text="⏱️ Thời gian: 00:00",
                             font=("Arial", 10, "bold"),
                             bg=COLORS["bg_primary"],
                             fg=COLORS["accent_blue"])
player_timer_label.pack(pady=3)

player_input_frame = tk.Frame(player_frame, bg=COLORS["bg_primary"])
tk.Label(player_input_frame,
        text="Nhập 3 chữ số của bạn:",
        font=("Arial", 12),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_primary"]).pack(pady=3)

player_guess_entry_container = tk.Frame(player_input_frame, bg=COLORS["bg_primary"])
player_guess_entry = tk.Entry(player_guess_entry_container,
                             width=8,
                             font=("Arial", 24),
                             justify='center',
                             bg=COLORS["bg_card"],
                             fg=COLORS["text_accent"],
                             relief=tk.SOLID,
                             bd=2,
                             insertbackground=COLORS["text_accent"])
player_guess_entry.pack(side=tk.LEFT, padx=5)

player_guess_btn = tk.Button(player_guess_entry_container,
                            text="Đoán",
                            font=("Arial", 11, "bold"),
                            bg=COLORS["player"],
                            fg="white",
                            relief=tk.FLAT,
                            activebackground=COLORS["accent_blue"],
                            command=make_player_guess)
player_guess_btn.pack(side=tk.LEFT, padx=5)
player_guess_entry_container.pack()
player_input_frame.pack(pady=10)

player_result_label = tk.Label(player_frame,
                              text="",
                              font=("Arial", 12, "bold"),
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"],
                              height=2,
                              wraplength=550)
player_result_label.pack(pady=8)

player_history_frame = tk.Frame(player_frame, bg=COLORS["bg_primary"])
tk.Label(player_history_frame,
        text="📋 Lịch sử đoán:",
        font=("Arial", 11, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_secondary"]).pack(pady=3)

player_history_text = tk.Text(player_history_frame,
                             width=45,
                             height=10,
                             font=("Courier", 10),
                             bg=COLORS["bg_card"],
                             fg=COLORS["text_primary"],
                             relief=tk.SOLID,
                             bd=1)
player_history_text.pack(pady=3)
player_history_frame.pack(pady=10)

player_nav_frame = tk.Frame(player_frame, bg=COLORS["bg_primary"])

nav_row1 = tk.Frame(player_nav_frame, bg=COLORS["bg_primary"])
nav_row1.pack(pady=5)

tk.Button(nav_row1,
         text="🔄 Chơi lại",
         font=("Arial", 11),
         bg=COLORS["btn_success"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_green"],
         command=start_player_game).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row1,
         text="🏠 Trang chủ",
         font=("Arial", 11),
         bg=COLORS["btn_primary"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_blue"],
         command=lambda: show_page(home_frame)).pack(side=tk.LEFT, padx=5)

nav_row2 = tk.Frame(player_nav_frame, bg=COLORS["bg_primary"])
nav_row2.pack(pady=5)

tk.Button(nav_row2,
         text="📜 Lịch sử chơi",
         font=("Arial", 11),
         bg=COLORS["btn_warning"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_yellow"],
         command=view_history).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row2,
         text="🏆 Bảng xếp hạng",
         font=("Arial", 11),
         bg="#f59e0b",
         fg="white",
         relief=tk.FLAT,
         activebackground="#fbbf24",
         command=view_rankings).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row2,
         text="📖 Luật chơi",
         font=("Arial", 11),
         bg=COLORS["btn_info"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_purple"],
         command=show_rules_page).pack(side=tk.LEFT, padx=5)

player_nav_frame.pack(pady=10)

# ===== TRANG CHẾ ĐỘ MÁY CHƠI =====
computer_frame = tk.Frame(root, bg=COLORS["bg_primary"])

computer_header = tk.Frame(computer_frame, bg=COLORS["computer"], height=70)
computer_header.pack(fill=tk.X)
computer_header.pack_propagate(False)

tk.Label(computer_header, text="🤖 CHẾ ĐỘ MÁY CHƠI", 
         font=("Arial", 18, "bold"), bg=COLORS["computer"], fg="white").pack(pady=15)

main_container = tk.Frame(computer_frame, bg=COLORS["bg_primary"])
main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

left_column = tk.Frame(main_container, bg=COLORS["bg_primary"])
left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

computer_info_label = tk.Label(left_column,
                              text="",
                              font=("Arial", 12),
                              bg=COLORS["bg_primary"],
                              fg=COLORS["text_primary"])
computer_info_label.pack(pady=5)

computer_secret_label = tk.Label(left_column,
                                text="",
                                font=("Arial", 12, "bold"),
                                bg=COLORS["bg_primary"],
                                fg=COLORS["accent_red"])
computer_secret_label.pack(pady=3)

computer_status_label = tk.Label(left_column,
                                text="",
                                font=("Arial", 12),
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_secondary"])
computer_status_label.pack(pady=3)

computer_timer_label = tk.Label(left_column,
                               text="⏱️ Thời gian: 00:00",
                               font=("Arial", 10, "bold"),
                               bg=COLORS["bg_primary"],
                               fg=COLORS["accent_purple"])
computer_timer_label.pack(pady=3)

computer_possible_label = tk.Label(left_column,
                                  text="",
                                  font=("Arial", 11),
                                  bg=COLORS["bg_primary"],
                                  fg=COLORS["text_secondary"])
computer_possible_label.pack(pady=3)

computer_input_frame = tk.Frame(left_column, bg=COLORS["bg_primary"])
tk.Label(computer_input_frame,
        text="Số máy sẽ đoán:",
        font=("Arial", 12),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_primary"]).pack(pady=3)

computer_guess_entry_container = tk.Frame(computer_input_frame, bg=COLORS["bg_primary"])
computer_guess_entry = tk.Entry(computer_guess_entry_container,
                               width=8,
                               font=("Arial", 24),
                               justify='center',
                               bg=COLORS["bg_card"],
                               fg=COLORS["text_accent"],
                               relief=tk.SOLID,
                               bd=2,
                               insertbackground=COLORS["text_accent"])
computer_guess_entry.pack(side=tk.LEFT, padx=5)

computer_auto_btn = tk.Button(computer_guess_entry_container,
                             text="Máy đoán tiếp",
                             font=("Arial", 11, "bold"),
                             bg=COLORS["computer"],
                             fg="white",
                             relief=tk.FLAT,
                             activebackground=COLORS["accent_purple"],
                             command=computer_auto_guess)
computer_auto_btn.pack(side=tk.LEFT, padx=5)
computer_guess_entry_container.pack()
computer_input_frame.pack(pady=10)

computer_hint_frame = tk.Frame(left_column, bg=COLORS["bg_primary"])
tk.Label(computer_hint_frame,
        text="Chọn gợi ý cho máy:",
        font=("Arial", 12, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_secondary"]).pack(pady=5)

computer_hint_table_frame = tk.Frame(computer_hint_frame, bg=COLORS["bg_primary"])

computer_hint_none_btn = tk.Button(computer_hint_table_frame,
                                  text="Bagels (0 đúng)",
                                  font=("Arial", 10, "bold"),
                                  bg=COLORS["btn_danger"],
                                  fg="white",
                                  relief=tk.FLAT,
                                  width=15,
                                  height=2,
                                  activebackground=COLORS["accent_red"],
                                  command=lambda: give_hint_to_computer("none"))
computer_hint_none_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

computer_hint_correct_btn = tk.Button(computer_hint_table_frame,
                                     text="✅ Chính xác!",
                                     font=("Arial", 10, "bold"),
                                     bg=COLORS["btn_success"],
                                     fg="white",
                                     relief=tk.FLAT,
                                     width=15,
                                     height=2,
                                     activebackground=COLORS["accent_green"],
                                     command=lambda: give_hint_to_computer("correct"))
computer_hint_correct_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

hint_controls_frame = tk.Frame(computer_hint_table_frame, bg=COLORS["bg_primary"])
hint_controls_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

pico_control_frame = tk.Frame(hint_controls_frame, bg=COLORS["bg_primary"])
pico_control_frame.pack(fill=tk.X, padx=10, pady=5)

pico_title_frame = tk.Frame(pico_control_frame, bg=COLORS["bg_primary"])
pico_title_frame.pack(fill=tk.X, pady=3)

tk.Label(pico_title_frame, 
        text="Pico: (đúng số, sai vị trí)",
        font=("Arial", 10, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["accent_yellow"]).pack(side=tk.LEFT, anchor="w")

pico_counter_frame = tk.Frame(pico_control_frame, bg=COLORS["bg_primary"])
pico_counter_frame.pack(fill=tk.X, pady=3)

computer_pico_minus_btn = tk.Button(pico_counter_frame,
                                   text="  -  ",
                                   font=("Arial", 11, "bold"),
                                   bg=COLORS["accent_yellow"],
                                   fg=COLORS["bg_primary"],
                                   relief=tk.FLAT,
                                   width=6,
                                   state=tk.DISABLED,
                                   activebackground=COLORS["accent_yellow"],
                                   command=lambda: update_counter("pico", -1))
computer_pico_minus_btn.pack(side=tk.LEFT, padx=5)

computer_pico_label = tk.Label(pico_counter_frame,
                              text="Pico: 0",
                              font=("Arial", 12, "bold"),
                              bg=COLORS["bg_card"],
                              fg=COLORS["accent_yellow"],
                              relief=tk.SUNKEN,
                              bd=1,
                              width=6,
                              height=1)
computer_pico_label.pack(side=tk.LEFT, padx=5)

computer_pico_plus_btn = tk.Button(pico_counter_frame,
                                  text="  +  ",
                                  font=("Arial", 11, "bold"),
                                  bg=COLORS["accent_yellow"],
                                  fg=COLORS["bg_primary"],
                                  relief=tk.FLAT,
                                  width=6,
                                  activebackground=COLORS["accent_yellow"],
                                  command=lambda: update_counter("pico", 1))
computer_pico_plus_btn.pack(side=tk.LEFT, padx=5)

fermi_control_frame = tk.Frame(hint_controls_frame, bg=COLORS["bg_primary"])
fermi_control_frame.pack(fill=tk.X, padx=10, pady=5)

fermi_title_frame = tk.Frame(fermi_control_frame, bg=COLORS["bg_primary"])
fermi_title_frame.pack(fill=tk.X, pady=3)

tk.Label(fermi_title_frame, 
        text="Fermi: (đúng số, đúng vị trí)",
        font=("Arial", 10, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["accent_blue"]).pack(side=tk.LEFT, anchor="w")

fermi_counter_frame = tk.Frame(fermi_control_frame, bg=COLORS["bg_primary"])
fermi_counter_frame.pack(fill=tk.X, pady=3)

computer_fermi_minus_btn = tk.Button(fermi_counter_frame,
                                    text="  -  ",
                                    font=("Arial", 11, "bold"),
                                    bg=COLORS["accent_blue"],
                                    fg=COLORS["bg_primary"],
                                    relief=tk.FLAT,
                                    width=6,
                                    state=tk.DISABLED,
                                    activebackground=COLORS["accent_blue"],
                                    command=lambda: update_counter("fermi", -1))
computer_fermi_minus_btn.pack(side=tk.LEFT, padx=5)

computer_fermi_label = tk.Label(fermi_counter_frame,
                               text="Fermi: 0",
                               font=("Arial", 12, "bold"),
                               bg=COLORS["bg_card"],
                               fg=COLORS["accent_blue"],
                               relief=tk.SUNKEN,
                               bd=1,
                               width=6,
                               height=1)
computer_fermi_label.pack(side=tk.LEFT, padx=5)

computer_fermi_plus_btn = tk.Button(fermi_counter_frame,
                                   text="  +  ",
                                   font=("Arial", 11, "bold"),
                                   bg=COLORS["accent_blue"],
                                   fg=COLORS["bg_primary"],
                                   relief=tk.FLAT,
                                   width=6,
                                   activebackground=COLORS["accent_blue"],
                                   command=lambda: update_counter("fermi", 1))
computer_fermi_plus_btn.pack(side=tk.LEFT, padx=5)

computer_hint_table_frame.pack(pady=10)

computer_custom_hint_btn = tk.Button(computer_hint_frame,
                                    text="GỬI GỢI Ý NÀY",
                                    font=("Arial", 11, "bold"),
                                    bg=COLORS["computer"],
                                    fg="white",
                                    relief=tk.FLAT,
                                    width=20,
                                    height=2,
                                    activebackground=COLORS["accent_purple"],
                                    command=lambda: give_hint_to_computer("custom"))
computer_custom_hint_btn.pack(pady=10)

computer_hint_frame.pack(pady=10)

result_display_frame = tk.Frame(left_column, bg=COLORS["bg_primary"])
result_display_frame.pack(pady=8, fill=tk.X, expand=True)

result_center_frame = tk.Frame(result_display_frame, bg=COLORS["bg_primary"])
result_center_frame.pack(expand=True)

computer_result_label = tk.Label(result_center_frame,
                                text="",
                                font=("Arial", 12, "bold"),
                                bg=COLORS["bg_primary"],
                                fg=COLORS["text_primary"],
                                height=2,
                                wraplength=380,
                                justify=tk.CENTER)
computer_result_label.pack()

right_column = tk.Frame(main_container, bg=COLORS["bg_primary"])
right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

computer_history_frame = tk.Frame(right_column, bg=COLORS["bg_primary"])
tk.Label(computer_history_frame,
        text="📋 Lịch sử đoán:",
        font=("Arial", 11, "bold"),
        bg=COLORS["bg_primary"],
        fg=COLORS["text_secondary"]).pack(pady=3, anchor="w")

computer_history_text = tk.Text(computer_history_frame,
                               width=35,
                               height=15,
                               font=("Courier", 10),
                               bg=COLORS["bg_card"],
                               fg=COLORS["text_primary"],
                               relief=tk.SOLID,
                               bd=1)
computer_history_text.pack(pady=3, fill=tk.BOTH, expand=True)
computer_history_frame.pack(pady=10, fill=tk.BOTH, expand=True)

computer_nav_frame = tk.Frame(right_column, bg=COLORS["bg_primary"])
computer_nav_frame.pack(pady=10, fill=tk.X)

nav_row1 = tk.Frame(computer_nav_frame, bg=COLORS["bg_primary"])
nav_row1.pack(pady=5)

tk.Button(nav_row1,
         text="🔄 Chơi lại với số khác",
         font=("Arial", 11),
         bg=COLORS["btn_success"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_green"],
         command=start_computer_mode).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row1,
         text="🔄 Chơi lại với số này",
         font=("Arial", 11),
         bg=COLORS["accent_green"],
         fg="white",
         relief=tk.FLAT,
         activebackground="#10b981",
         command=lambda: start_computer_game_with_same_number()).pack(side=tk.LEFT, padx=5)

nav_row2 = tk.Frame(computer_nav_frame, bg=COLORS["bg_primary"])
nav_row2.pack(pady=5)

tk.Button(nav_row2,
         text="🔙 Quay lại nhập số",
         font=("Arial", 11),
         bg=COLORS["btn_primary"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_blue"],
         command=start_computer_mode).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row2,
         text="🏠 Trang chủ",
         font=("Arial", 11),
         bg=COLORS["btn_info"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_purple"],
         command=lambda: show_page(home_frame)).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row2,
         text="📜 Lịch sử chơi",
         font=("Arial", 11),
         bg=COLORS["btn_warning"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_yellow"],
         command=view_history).pack(side=tk.LEFT, padx=5)

tk.Button(nav_row2,
         text="📖 Luật chơi",
         font=("Arial", 11),
         bg=COLORS["computer"],
         fg="white",
         relief=tk.FLAT,
         activebackground=COLORS["accent_purple"],
         command=show_rules_page).pack(side=tk.LEFT, padx=5)

# ===== TRANG LUẬT CHƠI =====
rules_frame = tk.Frame(root, bg=COLORS["bg_primary"])

rules_header = tk.Frame(rules_frame, bg=COLORS["btn_warning"], height=70)
rules_header.pack(fill=tk.X)
rules_header.pack_propagate(False)

tk.Label(rules_header, text="📖 LUẬT CHƠI BAGELS", 
         font=("Arial", 18, "bold"), bg=COLORS["btn_warning"], fg="white").pack(pady=15)

rules_content = tk.Text(rules_frame,
                       width=70,
                       height=20,
                       font=("Arial", 11),
                       bg=COLORS["bg_card"],
                       fg=COLORS["text_primary"],
                       relief=tk.FLAT,
                       wrap=tk.WORD,
                       padx=15,
                       pady=15)
rules_content.pack(pady=15, padx=25, fill=tk.BOTH, expand=True)

rules_text = """🎯 LUẬT CHƠI BAGELS 🎯

Mục tiêu: Đoán số bí mật gồm 3 chữ số khác nhau.

📌 QUY TẮC CƠ BẢN:
1. Số bí mật gồm 3 chữ số từ 0-9
2. Các chữ số không trùng nhau
3. Bạn có 10 lượt đoán
4. Hệ thống TỰ ĐỘNG tính tổng thời gian chơi

🎮 CHẾ ĐỘ NGƯỜI CHƠI:
• Bạn sẽ là người đoán số bí mật do máy tạo ra
• Nhập 3 chữ số khác nhau vào ô và nhấn "Đoán"
• Máy sẽ đưa ra gợi ý dựa trên số bạn đoán
• Thắng khi đoán đúng số trong 10 lượt
• Điểm số: 1000 điểm cho mỗi lượt còn lại
• Thời gian được tính từ lúc bắt đầu game đến khi kết thúc

⏱️ HỆ THỐNG THỜI GIAN:
• Tính TỔNG thời gian chơi của cả game
• Bắt đầu tính khi bắt đầu game
• Dừng tính khi kết thúc game (thắng/thua/phát hiện gian lận)
• Hiển thị đồng hồ thời gian thực trong khi chơi
• Thời gian được lưu vào bảng xếp hạng để so sánh
• Nếu điểm bằng nhau, ưu tiên người chơi có thời gian NHANH HƠN

🤖 CHẾ ĐỘ MÁY CHƠI:
1. Bạn nhập số bí mật của mình (3 chữ số khác nhau)
2. Máy sẽ đưa ra số đoán
3. Bạn cung cấp gợi ý cho máy bằng cách:
  • Nhấn "Bagels" nếu không có số nào đúng
  • Nhấn "Chính xác!" nếu máy đoán đúng
  • Dùng nút +/- để chỉ định số lượng Pico/Fermi
4. Máy tiếp tục đoán dựa trên gợi ý của bạn

🔍 HỆ THỐNG PHÁT HIỆN GIAN LẬN THÔNG MINH:
• Hệ thống TỰ ĐỘNG PHÁT HIỆN GIAN LẬN mà không cần biết số bí mật
• Kiểm tra logic: Không thể có 4 Fermi trong 3 chữ số
• Kiểm tra tính nhất quán: Gợi ý không được mâu thuẫn với các lần trước
• Kiểm tra khả năng: Gợi ý không được loại bỏ tất cả khả năng còn lại
• Khi phát hiện gian lận: MÁY TỰ ĐỘNG THẮNG, lịch sử ghi rõ lý do

🏆 BẢNG XẾP HẠNG:
• Chỉ tính điểm cho chế độ Người chơi khi THẮNG
• Điểm = 1000 × (11 - số lượt đã dùng)
• Sắp xếp theo điểm cao nhất, nếu điểm bằng thì xếp theo thời gian nhanh hơn
• Top 10 người chơi xuất sắc nhất được lưu lại
• Hiển thị đầy đủ: Hạng, Điểm, Số lượt, Thời gian, Ngày chơi, Số bí mật

💡 HỆ THỐNG GỢI ý:
• BAGELS - Không có chữ số nào đúng
• PICO   - Có chữ số đúng nhưng sai vị trí
• FERMI  - Có chữ số đúng và đúng vị trí

📝 VÍ DỤ MINH HỌA:
Số bí mật: 456

• Đoán: 123 → Kết quả: Bagels (Không có chữ số nào đúng)
• Đoán: 456 → Kết quả: 🎉 CHÍNH XÁC! 🎉 (Tất cả đều đúng)
• Đoán: 645 → Kết quả: Pico Pico Pico (Cả 3 số đều đúng nhưng sai vị trí)
• Đoán: 465 → Kết quả: Fermi Fermi Pico (4 và 5 đúng vị trí, 6 sai vị trí)

Chúc bạn chơi vui vẻ và trở thành bậc thầy Bagels! 🎲"""

rules_content.insert("1.0", rules_text)
rules_content.config(state=tk.DISABLED)

nav_frame = tk.Frame(rules_frame, bg=COLORS["bg_primary"])
tk.Button(nav_frame,
         text="🔙 Quay về",
         font=("Arial", 11),
         bg=COLORS["btn_primary"],
         fg="white",
         relief=tk.FLAT,
         width=12,
         activebackground=COLORS["accent_blue"],
         command=lambda: show_page(home_frame)).pack(side=tk.LEFT, padx=5)

nav_frame.pack(pady=15)

# ===== KHUNG LỊCH SỬ CHUNG =====
history_frame = tk.Frame(root, bg=COLORS["bg_primary"])

history_title = tk.Label(history_frame,
                        text="📜 LỊCH SỬ CÁC LẦN CHƠI",
                        font=("Arial", 18, "bold"),
                        bg=COLORS["bg_primary"],
                        fg=COLORS["text_accent"])
history_title.pack(pady=15)

history_subtitle = tk.Label(history_frame,
                           text="30 lần chơi gần nhất (lưu tự động vào file)",
                           font=("Arial", 12),
                           bg=COLORS["bg_primary"],
                           fg=COLORS["text_secondary"])
history_subtitle.pack(pady=3)

history_container = tk.Frame(history_frame, bg=COLORS["bg_primary"])
history_container.pack(pady=15, padx=15, fill=tk.BOTH, expand=True)

back_btn = tk.Button(history_frame,
                    text="🔙 Quay về",
                    font=("Arial", 11),
                    bg=COLORS["btn_primary"],
                    fg="white",
                    relief=tk.FLAT,
                    width=12,
                    activebackground=COLORS["accent_blue"],
                    command=go_back_from_history)
back_btn.pack(pady=15)

# ========== CHẠY CHƯƠNG TRÌNH ==========
load_data()
show_page(home_frame)

update_player_timer()
update_computer_timer()

def on_closing():
    save_data()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()