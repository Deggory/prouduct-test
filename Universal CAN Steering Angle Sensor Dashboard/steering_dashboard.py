import tkinter as tk

    angle_label.config(text=f"{angle_value:7.1f}°")
    rate_label.config(text=f"Rate: {rate_value} deg/s")
    packet_label.config(text=f"Packets: {packet_count}")
    minmax_label.config(text=f"Min: {min_angle:7.1f}°   Max: {max_angle:7.1f}°")
    mcp_label.config(text=f"MCP2515: {mcp_status}")
    can_label.config(text=f"CAN: {can_status}")
    sniff_label.config(text=last_sniff[:100])
    detect_label.config(
        text=f"Detected Steering ID: {detected_id}  Confidence: {detect_confidence}"
    )

    root.after(50, update_gui)


# ================= GUI LAYOUT =================
root = tk.Tk()
root.title("Universal Steering CAN Dashboard")
root.geometry("600x650")

header = tk.Label(root, text=f"ESP32 Port: {PORT}", font=("Arial", 14, "bold"))
header.pack(pady=5)

canvas = tk.Canvas(root, width=500, height=300)
canvas.pack()

# Gauge arc + zero line
canvas.create_arc(100, 60, 400, 360, start=45, extent=270, style="arc", width=3)
canvas.create_line(250, 60, 250, 300, dash=(4, 2))

angle_label = tk.Label(root, text="0.0°", font=("Arial", 36, "bold"))
angle_label.pack()

rate_label = tk.Label(root, text="Rate: 0 deg/s", font=("Arial", 18))
rate_label.pack()

packet_label = tk.Label(root, text="Packets: 0", font=("Arial", 18))
packet_label.pack()

minmax_label = tk.Label(root, text="Min: 0.0°   Max: 0.0°", font=("Arial", 18, "bold"))
minmax_label.pack()

mcp_label = tk.Label(root, text="MCP2515: UNKNOWN", font=("Arial", 18, "bold"))
mcp_label.pack()

can_label = tk.Label(root, text="CAN: FAIL", font=("Arial", 18, "bold"))
can_label.pack()

sniff_label = tk.Label(root, text="No frames yet", font=("Courier", 10), wraplength=550)
sniff_label.pack(pady=10)

detect_label = tk.Label(
    root,
    text="Detected Steering ID: None  Confidence: LOW",
    font=("Arial", 16, "bold")
)
detect_label.pack(pady=10)

# Start serial thread
threading.Thread(target=serial_reader, daemon=True).start()
update_gui()

try:
    root.mainloop()
finally:
    running = False
    ser.close()
