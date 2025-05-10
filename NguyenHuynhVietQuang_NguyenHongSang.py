import heapq
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MangGiaoThong:
    """Lớp quản lý mô hình mạng giao thông"""
    
    def __init__(self):
        """Khởi tạo mạng giao thông rỗng"""
        self.do_thi = {}  # Danh sách kề
        self.ten_nut = {}  # Tên của các nút
    
    def them_nut(self, id_nut, ten=""):
        """Thêm một nút vào mạng giao thông"""
        if id_nut not in self.do_thi:
            self.do_thi[id_nut] = {}
            self.ten_nut[id_nut] = ten if ten else f"Nút {id_nut}"
            return True
        return False
    
    def them_duong(self, id_nut1, id_nut2, trong_so):
        """Thêm một đường đi giữa hai nút với trọng số cho trước"""
        if id_nut1 in self.do_thi and id_nut2 in self.do_thi:
            self.do_thi[id_nut1][id_nut2] = trong_so
            return True
        return False
    
    def xoa_nut(self, id_nut):
        """Xóa một nút khỏi mạng giao thông"""
        if id_nut in self.do_thi:
            del self.do_thi[id_nut]
            del self.ten_nut[id_nut]
            # Xóa tất cả các đường đi đến nút này
            for nut in self.do_thi:
                if id_nut in self.do_thi[nut]:
                    del self.do_thi[nut][id_nut]
            return True
        return False
    
    def xoa_duong(self, id_nut1, id_nut2):
        """Xóa đường đi giữa hai nút"""
        if id_nut1 in self.do_thi and id_nut2 in self.do_thi[id_nut1]:
            del self.do_thi[id_nut1][id_nut2]
            return True
        return False
    
    def danh_sach_nut(self):
        """Trả về danh sách tất cả các nút trong mạng"""
        return list(self.do_thi.keys())
    
    def dijkstra(self, nut_xuat_phat, nut_dich=None):
        """
        Thuật toán Dijkstra tìm đường đi ngắn nhất từ nut_xuat_phat
        đến tất cả các nút khác hoặc đến nut_dich (nếu được chỉ định)
        """
        # Kiểm tra đầu vào
        if nut_xuat_phat not in self.do_thi:
            return None, None
        
        # Khởi tạo
        khoang_cach = {nut: float('infinity') for nut in self.do_thi}
        khoang_cach[nut_xuat_phat] = 0
        nut_truoc = {nut: None for nut in self.do_thi}
        da_xet = set()
        
        # Hàng đợi ưu tiên
        hang_doi = [(0, nut_xuat_phat)]
        
        while hang_doi:
            # Lấy nút có khoảng cách nhỏ nhất
            k_cach_hien_tai, nut_hien_tai = heapq.heappop(hang_doi)
            
            # Nếu đã tìm thấy đường đi đến nút đích
            if nut_dich is not None and nut_hien_tai == nut_dich:
                break
                
            # Nếu nút đã được xét, bỏ qua
            if nut_hien_tai in da_xet:
                continue
                
            # Đánh dấu nút hiện tại là đã xét
            da_xet.add(nut_hien_tai)
            
            # Cập nhật khoảng cách cho các nút kề
            for nut_ke, trong_so in self.do_thi[nut_hien_tai].items():
                if nut_ke in da_xet:
                    continue
                    
                k_cach_moi = k_cach_hien_tai + trong_so
                
                if k_cach_moi < khoang_cach[nut_ke]:
                    khoang_cach[nut_ke] = k_cach_moi
                    nut_truoc[nut_ke] = nut_hien_tai
                    heapq.heappush(hang_doi, (k_cach_moi, nut_ke))
        
        return khoang_cach, nut_truoc
    
    def duong_di_ngan_nhat(self, nut_xuat_phat, nut_dich):
        """Tìm đường đi ngắn nhất từ nut_xuat_phat đến nut_dich"""
        # Kiểm tra đầu vào
        if (nut_xuat_phat not in self.do_thi or 
            nut_dich not in self.do_thi):
            return None, None
            
        # Thuật toán Dijkstra
        khoang_cach, nut_truoc = self.dijkstra(nut_xuat_phat, nut_dich)
        
        if khoang_cach[nut_dich] == float('infinity'):
            return None, None  # Không có đường đi
            
        # Xây dựng đường đi
        duong_di = []
        nut_hien_tai = nut_dich
        
        while nut_hien_tai is not None:
            duong_di.append(nut_hien_tai)
            nut_hien_tai = nut_truoc[nut_hien_tai]
            
        duong_di.reverse()  # Đảo ngược để có thứ tự từ xuất phát đến đích
        
        return duong_di, khoang_cach[nut_dich]


class GiaoDienNguoiDung(tk.Tk):
    """Lớp quản lý giao diện người dùng"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Tìm Đường Đi Ngắn Nhất trong Mạng Giao Thông")
        self.geometry("1200x800")
        self.configure(bg='#ccf2ff')  # Màu nền


        self.mang_giao_thong = MangGiaoThong()
        self.nx_graph = nx.DiGraph()
        self.pos = None  # Lưu vị trí các nút để sử dụng lại
        
        self._tao_giao_dien()
        self._tao_du_lieu_mau()
        self._cap_nhat_do_thi()
        
    def _tao_giao_dien(self):
        """Tạo các thành phần giao diện người dùng"""
        style = ttk.Style()
        style.configure("TFrame", background="#ccf2ff")
        style.configure("TLabelframe", background="#ccf2ff")
        style.configure("TLabel", background="#ccf2ff")

        # Tạo frame chính
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame điều khiển bên trái
        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Frame đồ họa bên phải
        graph_frame = ttk.LabelFrame(main_frame, text="Mạng giao thông")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tạo đồ thị
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Thêm thanh công cụ zoom/pan
        self.toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        self.toolbar.update()
        self.toolbar.pack(fill=tk.X)
        
        # Các nút điều khiển
        ttk.Button(control_frame, text="Thêm nút", 
                  command=self._them_nut).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Thêm đường đi", 
                  command=self._them_duong).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Xóa nút", 
                  command=self._xoa_nut).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Xóa đường đi", 
                  command=self._xoa_duong).pack(fill=tk.X, pady=5)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Frame tìm đường đi
        path_frame = ttk.LabelFrame(control_frame, text="Tìm đường đi ngắn nhất")
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Nút xuất phát:").pack(anchor=tk.W)
        self.cb_start = ttk.Combobox(path_frame, state="readonly")
        self.cb_start.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Nút đích:").pack(anchor=tk.W)
        self.cb_end = ttk.Combobox(path_frame, state="readonly")
        self.cb_end.pack(fill=tk.X, pady=5)
        
        ttk.Button(path_frame, text="Tìm đường đi", 
                  command=self._tim_duong_di).pack(fill=tk.X, pady=10)
        
        # Frame kết quả
        result_frame = ttk.LabelFrame(control_frame, text="Kết quả")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
    def _cap_nhat_do_thi(self):
        """Cập nhật biểu diễn đồ thị"""
        self.nx_graph.clear()
        
        # Thêm các nút vào đồ thị NetworkX
        for id_nut, ten in self.mang_giao_thong.ten_nut.items():
            self.nx_graph.add_node(id_nut, label=ten)
        
        # Thêm các cạnh vào đồ thị NetworkX
        for id_nut1 in self.mang_giao_thong.do_thi:
            for id_nut2, trong_so in self.mang_giao_thong.do_thi[id_nut1].items():
                self.nx_graph.add_edge(id_nut1, id_nut2, weight=trong_so)
        
        # Cập nhật combobox
        nut_list = self.mang_giao_thong.danh_sach_nut()
        nut_names = [f"{id_nut}: {self.mang_giao_thong.ten_nut[id_nut]}" for id_nut in nut_list]
        
        self.cb_start['values'] = nut_names
        self.cb_end['values'] = nut_names
        
        if nut_names:
            self.cb_start.current(0)
            self.cb_end.current(min(1, len(nut_names)-1))
        
        # Vẽ đồ thị
        self.ax.clear()
        
        # Tính và lưu vị trí các nút
        self.pos = nx.spring_layout(self.nx_graph, seed=42)  # Sử dụng seed để cố định layout
        
        # Vẽ các nút
        nx.draw_networkx_nodes(self.nx_graph, self.pos, node_size=500, 
                              node_color='lightblue', ax=self.ax)
        
        # Vẽ các cạnh
        nx.draw_networkx_edges(self.nx_graph, self.pos, width=1, 
                              edge_color='gray', arrows=True, ax=self.ax)
        
        # Vẽ nhãn nút
        labels = {node: data['label'] for node, data in self.nx_graph.nodes(data=True)}
        nx.draw_networkx_labels(self.nx_graph, self.pos, labels=labels, font_size=10, ax=self.ax)
        
        # Vẽ trọng số cạnh
        edge_labels = {(u, v): d['weight'] for u, v, d in self.nx_graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.nx_graph, self.pos, edge_labels=edge_labels, 
                                    font_size=8, ax=self.ax)
        
        self.ax.set_axis_off()
        self.canvas.draw()
    
    def _ve_duong_di(self, duong_di):
        """Vẽ đường đi ngắn nhất trên đồ thị"""
        if not duong_di:
            self._cap_nhat_do_thi()  # Vẽ lại đồ thị gốc nếu không có đường đi
            return
            
        # Vẽ lại đồ thị gốc trước
        self.ax.clear()
        
        # Vẽ các nút
        nx.draw_networkx_nodes(self.nx_graph, self.pos, node_size=500, 
                              node_color='lightblue', ax=self.ax)
        
        # Vẽ tất cả các cạnh với màu xám
        nx.draw_networkx_edges(self.nx_graph, self.pos, width=1, 
                              edge_color='gray', arrows=True, ax=self.ax)
        
        # Vẽ nhãn nút
        labels = {node: data['label'] for node, data in self.nx_graph.nodes(data=True)}
        nx.draw_networkx_labels(self.nx_graph, self.pos, labels=labels, font_size=10, ax=self.ax)
        
        # Vẽ trọng số cạnh
        edge_labels = {(u, v): d['weight'] for u, v, d in self.nx_graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.nx_graph, self.pos, edge_labels=edge_labels, 
                                    font_size=8, ax=self.ax)
        
        # Tạo danh sách các cạnh trong đường đi
        path_edges = list(zip(duong_di[:-1], duong_di[1:]))
        
        # Vẽ các cạnh trong đường đi với màu đỏ và độ dày lớn hơn
        nx.draw_networkx_edges(self.nx_graph, self.pos, 
                              edgelist=path_edges,
                              width=3, edge_color='red', 
                              arrows=True, ax=self.ax)
        
        # Đánh dấu nút xuất phát (xanh lá) và nút đích (đỏ)
        nx.draw_networkx_nodes(self.nx_graph, self.pos, 
                              nodelist=[duong_di[0]],
                              node_size=500, node_color='green', 
                              ax=self.ax)
        nx.draw_networkx_nodes(self.nx_graph, self.pos, 
                              nodelist=[duong_di[-1]],
                              node_size=500, node_color='red', 
                              ax=self.ax)
        
        self.ax.set_axis_off()
        self.canvas.draw()
    
    def _them_nut(self):
        """Xử lý sự kiện thêm nút"""
        id_nut = simpledialog.askinteger("Thêm nút", "Nhập ID nút:",
                                      parent=self, minvalue=1)
        if id_nut is not None:
            ten_nut = simpledialog.askstring("Thêm nút", "Nhập tên nút:",
                                          parent=self)
            if self.mang_giao_thong.them_nut(id_nut, ten_nut):
                self._cap_nhat_do_thi()
                messagebox.showinfo("Thành công", f"Đã thêm nút {id_nut}")
            else:
                messagebox.showerror("Lỗi", f"Nút {id_nut} đã tồn tại")
    
    def _them_duong(self):
        """Xử lý sự kiện thêm đường đi"""
        nut_list = self.mang_giao_thong.danh_sach_nut()
        if len(nut_list) < 2:
            messagebox.showerror("Lỗi", "Cần ít nhất 2 nút để thêm đường đi")
            return
            
        nut_names = [f"{id_nut}: {self.mang_giao_thong.ten_nut[id_nut]}" for id_nut in nut_list]
        
        id_nut1 = simpledialog.askinteger("Thêm đường đi", "Nhập ID nút xuất phát:",
                                       parent=self, minvalue=1)
        if id_nut1 is None or id_nut1 not in nut_list:
            messagebox.showerror("Lỗi", "Nút xuất phát không hợp lệ")
            return
            
        id_nut2 = simpledialog.askinteger("Thêm đường đi", "Nhập ID nút đích:",
                                       parent=self, minvalue=1)
        if id_nut2 is None or id_nut2 not in nut_list:
            messagebox.showerror("Lỗi", "Nút đích không hợp lệ")
            return
            
        trong_so = simpledialog.askfloat("Thêm đường đi", "Nhập trọng số (chi phí):",
                                       parent=self, minvalue=0.1)
        if trong_so is None:
            return
            
        if self.mang_giao_thong.them_duong(id_nut1, id_nut2, trong_so):
            self._cap_nhat_do_thi()
            messagebox.showinfo("Thành công", 
                              f"Đã thêm đường đi từ {id_nut1} đến {id_nut2} với chi phí {trong_so}")
        else:
            messagebox.showerror("Lỗi", "Không thể thêm đường đi")
    
    def _xoa_nut(self):
        """Xử lý sự kiện xóa nút"""
        nut_list = self.mang_giao_thong.danh_sach_nut()
        if not nut_list:
            messagebox.showerror("Lỗi", "Không có nút nào để xóa")
            return
            
        id_nut = simpledialog.askinteger("Xóa nút", "Nhập ID nút cần xóa:",
                                      parent=self)
        if id_nut is not None:
            if self.mang_giao_thong.xoa_nut(id_nut):
                self._cap_nhat_do_thi()
                messagebox.showinfo("Thành công", f"Đã xóa nút {id_nut}")
            else:
                messagebox.showerror("Lỗi", f"Nút {id_nut} không tồn tại")
    
    def _xoa_duong(self):
        """Xử lý sự kiện xóa đường đi"""
        nut_list = self.mang_giao_thong.danh_sach_nut()
        if len(nut_list) < 2:
            messagebox.showerror("Lỗi", "Cần ít nhất 2 nút để xóa đường đi")
            return
            
        id_nut1 = simpledialog.askinteger("Xóa đường đi", "Nhập ID nút xuất phát:",
                                       parent=self)
        if id_nut1 is None:
            return
            
        id_nut2 = simpledialog.askinteger("Xóa đường đi", "Nhập ID nút đích:",
                                       parent=self)
        if id_nut2 is None:
            return
            
        if self.mang_giao_thong.xoa_duong(id_nut1, id_nut2):
            self._cap_nhat_do_thi()
            messagebox.showinfo("Thành công", 
                              f"Đã xóa đường đi từ {id_nut1} đến {id_nut2}")
        else:
            messagebox.showerror("Lỗi", "Đường đi không tồn tại")
    
    def _tim_duong_di(self):
        """Xử lý sự kiện tìm đường đi ngắn nhất"""
        if not self.cb_start.get() or not self.cb_end.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn nút xuất phát và nút đích")
            return
            
        # Lấy ID nút từ combobox
        id_start = int(self.cb_start.get().split(':')[0])
        id_end = int(self.cb_end.get().split(':')[0])
        
        if id_start == id_end:
            messagebox.showerror("Lỗi", "Nút xuất phát và nút đích phải khác nhau")
            return
            
        # Tìm đường đi ngắn nhất
        duong_di, chi_phi = self.mang_giao_thong.duong_di_ngan_nhat(id_start, id_end)
        
        if duong_di is None:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Không tìm thấy đường đi từ {id_start} đến {id_end}")
            return
            
        # Hiển thị kết quả
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Đường đi ngắn nhất từ {id_start} đến {id_end}:\n\n")
        
        path_str = ""
        for i, nut in enumerate(duong_di):
            path_str += f"{nut}: {self.mang_giao_thong.ten_nut[nut]}"
            if i < len(duong_di) - 1:
                trong_so = self.mang_giao_thong.do_thi[nut][duong_di[i+1]]
                path_str += f" --({trong_so})--> "
        
        self.result_text.insert(tk.END, path_str + "\n\n")
        self.result_text.insert(tk.END, f"Tổng chi phí: {chi_phi}")
        
        # Vẽ đường đi trên đồ thị
        self._ve_duong_di(duong_di)
    
    def _tao_du_lieu_mau(self):
        """Tạo dữ liệu mẫu cho mạng giao thông"""
        # Thêm các nút
        self.mang_giao_thong.them_nut(1, "Trung tâm thành phố")
        self.mang_giao_thong.them_nut(2, "Khu công nghiệp")
        self.mang_giao_thong.them_nut(3, "Khu dân cư A")
        self.mang_giao_thong.them_nut(4, "Khu dân cư B")
        self.mang_giao_thong.them_nut(5, "Sân bay")
        self.mang_giao_thong.them_nut(6, "Bến xe")
        self.mang_giao_thong.them_nut(7, "Trung tâm thương mại")
        self.mang_giao_thong.them_nut(8, "Nhà ga xe lửa")
        
        # Thêm các đường đi
        self.mang_giao_thong.them_duong(1, 3, 4)
        self.mang_giao_thong.them_duong(1, 4, 7)
        self.mang_giao_thong.them_duong(1, 6, 4)
        self.mang_giao_thong.them_duong(1, 7, 6)
        self.mang_giao_thong.them_duong(2, 5, 5)
        self.mang_giao_thong.them_duong(2, 4, 7)
        self.mang_giao_thong.them_duong(3, 5, 4)
        self.mang_giao_thong.them_duong(3, 2, 6)
        self.mang_giao_thong.them_duong(4, 6, 4)
        self.mang_giao_thong.them_duong(5, 7, 7)
        self.mang_giao_thong.them_duong(6, 3, 4)
        self.mang_giao_thong.them_duong(6, 2, 6)
        self.mang_giao_thong.them_duong(7, 3, 5)
        self.mang_giao_thong.them_duong(8, 1, 5)
        self.mang_giao_thong.them_duong(8, 4, 6)
        self.mang_giao_thong.them_duong(8, 7, 7)
        # Thêm các đường hướng ngược lạilại
        self.mang_giao_thong.them_duong(3, 1, 4)
        self.mang_giao_thong.them_duong(4, 1, 7)
        self.mang_giao_thong.them_duong(6, 1, 4)
        self.mang_giao_thong.them_duong(7, 1, 6)
        self.mang_giao_thong.them_duong(5, 2, 5)
        self.mang_giao_thong.them_duong(4, 2, 7)
        self.mang_giao_thong.them_duong(5, 3, 4)
        self.mang_giao_thong.them_duong(2, 3, 6)
        self.mang_giao_thong.them_duong(6, 4, 4)
        self.mang_giao_thong.them_duong(7, 5, 7)
        self.mang_giao_thong.them_duong(3, 6, 4)
        self.mang_giao_thong.them_duong(2, 6, 6)
        self.mang_giao_thong.them_duong(3, 7, 5)
        self.mang_giao_thong.them_duong(1, 8, 5)
        self.mang_giao_thong.them_duong(4, 8, 6)
        self.mang_giao_thong.them_duong(7, 8, 7)


def main():
    """Hàm chính khởi chạy ứng dụng"""
    app = GiaoDienNguoiDung()
    app.mainloop()


if __name__ == "__main__":
    main()